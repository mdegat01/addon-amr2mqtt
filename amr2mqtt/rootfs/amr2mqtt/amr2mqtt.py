#!/usr/bin/env python3
"""
Runs rtlamr to watch for broadcasts from power meter(s). Passings readings
found to MQTT at topic `amr2mqtt/{meter_ID}`. If meter ID
is a watched one, processes its reading using settings first.

"""
from datetime import timedelta, datetime, timezone
import logging
import subprocess
import signal
import sys
import time
import json
import re
import math
import paho.mqtt.client as mqtt
import settings
from dateutil import parser

CATEGORY_DIAGNOSTIC = "diagnostic"
LAST_INTERVAL_ATTR = "LastIntervalConsumption"
CONSUMPTION_FIELD = "Consumption"
ID_FIELD = "ID"
INTERVAL_FIELD = "DifferentialConsumptionIntervals"
INTERVAL_ID_FIELD = "ConsumptionIntervalCount"
INTERVAL_START_FIELD = "IntervalStart"
IDM_TIME_OFFSET_FIELD = "TransmitTimeOffset"
IDM_ID_FIELD = "ERTSerialNumber"
IDM_CONSUMPTION_FIELD = "LastConsumptionCount"
NETIDM_CONSUMPTION_FIELD = "LastConsumptionNet"
SCMPLUS_ID_FIELD = "EndpointID"
LAST_SEEN_ATTR = "'last_seen': value_json.last_seen"
ALL_IDM = [
    "Preamble",
    "PacketLength",
    "HammingCode",
    "ApplicationVersion",
    "ERTType",
    INTERVAL_ID_FIELD,
    IDM_TIME_OFFSET_FIELD,
    "SerialNumberCRC",
    "PacketCRC",
]
ATTRIBUTES = {
    "idm": [
        "ModuleProgrammingState",
        "TamperCounters",
        "AsynchronousCounters",
        "PowerOutageFlags",
    ]
    + ALL_IDM,
    "netidm": [
        "ProgrammingState",
        "LastGeneration",
        "LastConsumption",
    ]
    + ALL_IDM,
    "r900": [
        "Unkn1",
        "NoUse",
        "BackFlow",
        "Unkn3",
        "Leak",
        "LeakNow",
        "checksum",
    ],
    "scm": [
        "Type",
        "TamperPhy",
        "TamperEnc",
        "ChecksumVal",
    ],
    "scm+": [
        "FrameSync",
        "ProtocolID",
        "EndpointType",
        "Tamper",
        "PacketCRC",
    ],
}


def shutdown(**_):
    """Disconnect MQTT client, stop rtlamr and exit."""
    mqttc.publish(
        topic=settings.MQTT_AVAILABILTY_TOPIC,
        payload="offline",
        retain=True,
    )
    logging.info("Disconnecting from MQTT broker")
    mqttc.loop_stop()
    mqttc.disconnect()
    stop_rtlamr()
    sys.exit(0)


def stop_rtlamr():
    """Stop and hard kill opened rtlamr process."""
    logging.info("Shutting down rtlamr")
    rtlamr.send_signal(15)
    time.sleep(1)
    rtlamr.send_signal(9)


def start_rtlamr():
    """Start rtlamr program."""
    rtlamr_cmd = [
        settings.RTLAMR,
        f"-msgtype={settings.WATCHED_PROTOCOLS}",
        "-format=json",
    ]

    # Add ID filter if we have a list of IDs to watch
    if settings.WATCHED_PROTOCOLS != "all":
        rtlamr_cmd += [f"-filterid={settings.WATCHED_METERS}"]

    logging.info("Starting rtlamr")
    return subprocess.Popen(
        rtlamr_cmd,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )


def on_mqtt_connect(client, userdata, flags, result):  # pylint: disable=unused-argument
    """Send online message on connect."""
    if result == 0:
        client.publish(
            topic=settings.MQTT_AVAILABILTY_TOPIC,
            payload="online",
            retain=True,
        )
    else:
        error_log = "MQTT Broker refused connection - %s (result code %s)"
        if result == 1:
            logging.error(error_log, "Incorrect protocol version", result)
        elif result == 2:
            logging.error(error_log, "Invalid client identifier", result)
        elif result == 3:
            logging.error(error_log, "Server unavailable", result)
        elif result == 4:
            logging.error(error_log, "Bad username or password", result)
        elif result == 5:
            logging.error(error_log, "Not authorised", result)
        else:
            logging.error(error_log, "Unknown error", result)

        stop_rtlamr()
        sys.exit(0)


def create_mqtt_client():
    """Create MQTT client with TLS and auth if necessary."""
    client = mqtt.Client(client_id=settings.MQTT_CLIENT_ID)
    client.on_connect = on_mqtt_connect
    client.will_set(
        topic=settings.MQTT_AVAILABILTY_TOPIC,
        payload="offline",
        qos=1,
        retain=True,
    )

    if settings.MQTT_CA_CERT:
        client.tls_set(
            ca_certs=settings.MQTT_CA_CERT,
            certfile=settings.MQTT_CERTFILE,
            keyfile=settings.MQTT_KEYFILE,
        )

    if settings.MQTT_USERNAME:
        client.username_pw_set(
            username=settings.MQTT_USERNAME,
            password=settings.MQTT_PASSWORD,
        )

    logging.info(
        "Connecting to MQTT broker at %s:%s", settings.MQTT_HOST, settings.MQTT_PORT
    )
    client.connect(
        host=settings.MQTT_HOST,
        port=settings.MQTT_PORT,
        keepalive=60,
    )
    return client


def create_interval_sensor(meter_id, meter, device_name, device_id):
    """Create discovery message for interval consumption sensor."""
    last_seen_attr = f"{LAST_SEEN_ATTR}," if settings.LAST_SEEN_ENABLED else ""

    return set_consumption_details(
        payload={
            "enabled_by_default": True,
            "name": f"{device_name} Last Interval Consumption",
            "unique_id": f"{device_id}_{LAST_INTERVAL_ATTR}",
            "value_template": f"{{{{ value_json.{INTERVAL_FIELD}[0] }}}}",
            "json_attributes_topic": f"{settings.MQTT_BASE_TOPIC}/{meter_id}",
            "json_attributes_template": (
                "{{ {"
                f"'{INTERVAL_FIELD}': value_json.{INTERVAL_FIELD},"
                f"'{INTERVAL_START_FIELD}': value_json.{INTERVAL_START_FIELD},"
                f"{last_seen_attr}"
                f"'last_reset': value_json.{INTERVAL_START_FIELD}"
                "} | tojson }}"
            ),
        },
        meter=meter,
    )


def set_consumption_details(payload, meter):
    """Set discovery details for a consumption sensor."""
    payload["state_class"] = "total"
    if "type" in meter:
        if meter["type"] == "gas":
            payload["device_class"] = "gas"
        elif meter["type"] == "energy":
            payload["device_class"] = "energy"
        else:
            payload["icon"] = "mdi:water"

    if "unit_of_measurement" in meter:
        payload["unit_of_measurement"] = meter["unit_of_measurement"]

    return payload


def create_sensor(attribute, device_name, device_id, enabled=True, category=None):
    """Create generic discovery message to make reading attribute into sensor."""
    # Turn camelcase into spaces
    name = re.sub(r"([^A-Z]|ERT)([A-Z])", r"\1 \2", attribute)
    sensor = {
        "enabled_by_default": enabled,
        "name": f"{device_name} {name}",
        "state_class": "measurement",
        "unique_id": f"{device_id}_{attribute}",
        "value_template": f"{{{{ value_json.{attribute} }}}}",
    }

    if category:
        sensor["entity_category"] = category

    if settings.LAST_SEEN_ENABLED:
        sensor[
            "json_attributes_template"
        ] = f"{{{{ {{ {LAST_SEEN_ATTR} }} | tojson }}}}"

    return sensor


def publish_sensor_discovery(meter_id, device, attribute, payload):
    """Publish discovery message to make reading attribute into sensor."""
    base_payload = {
        "availability": [
            {
                "topic": settings.MQTT_AVAILABILTY_TOPIC,
            }
        ],
        "device": device,
        "state_topic": f"{settings.MQTT_BASE_TOPIC}/{meter_id}",
        "platform": "mqtt",
    }

    mqttc.publish(
        topic=f"{settings.HA_DISCOVERY_TOPIC}/sensor/{meter_id}/{attribute}/config",
        payload=json.dumps(payload | base_payload),
        retain=True,
    )


def send_discovery_messages():
    """Send discovery messages to create sensors for each watched meter."""
    for meter_id, meter in settings.METERS.items():
        device_id = f"amr2mqtt_{meter_id}"
        device_name = meter.get("name", meter_id)
        protocol = meter["protocol"]
        device = {
            "identifiers": [device_id],
            "name": device_name,
            "sw_version": settings.SW_VERSION,
            "via_device": settings.VIA_DEVICE,
        }

        if "manufacturer" in meter:
            device["manufacturer"] = meter["manufacturer"]

        if "model" in meter:
            device["model"] = meter["model"]

        # All meters have a consumption sensor
        consumption = set_consumption_details(
            payload=create_sensor(
                attribute=CONSUMPTION_FIELD,
                device_name=device_name,
                device_id=device_id,
            ),
            meter=meter,
        )
        publish_sensor_discovery(
            meter_id=meter_id,
            device=device,
            attribute=CONSUMPTION_FIELD,
            payload=consumption,
        )

        # IDM meters have interval consumption
        if protocol in ["idm", "netidm"]:
            publish_sensor_discovery(
                meter_id=meter_id,
                device=device,
                attribute=LAST_INTERVAL_ATTR,
                payload=create_interval_sensor(
                    meter_id=meter_id,
                    meter=meter,
                    device_name=device_name,
                    device_id=device_id,
                ),
            )

        # Create disabled sensors from all other attributes so people can enable if they wish
        for attr in ATTRIBUTES[protocol]:
            publish_sensor_discovery(
                meter_id=meter_id,
                device=device,
                attribute=attr,
                payload=create_sensor(
                    attribute=attr,
                    device_name=device_name,
                    device_id=device_id,
                    enabled=False,
                    category=CATEGORY_DIAGNOSTIC,
                ),
            )


def adjust_reading(
    reading_time,
    meter_id,
    reading,
    consumption_field,
    idm_interval=None,
):
    """Convert consumption and interval data using configured multiplier."""
    meter = settings.METERS.get(meter_id, {})
    multiplier = meter.get("multiplier", 1)
    precision = meter.get("precision", -1)

    if precision > -1:
        convert = lambda value: round(value * multiplier, precision)
    else:
        convert = lambda value: value * multiplier

    reading[CONSUMPTION_FIELD] = convert(reading[consumption_field])

    if idm_interval is not None:
        reading[INTERVAL_FIELD] = [
            convert(interval) for interval in reading[INTERVAL_FIELD]
        ]

        if idm_interval.get(INTERVAL_ID_FIELD, -1) == reading[INTERVAL_ID_FIELD]:
            reading[INTERVAL_START_FIELD] = idm_interval[INTERVAL_START_FIELD]
        else:
            interval_seconds = reading[IDM_TIME_OFFSET_FIELD] / 16
            interval_start = reading_time - timedelta(seconds=interval_seconds)
            reading[INTERVAL_START_FIELD] = interval_start.isoformat()
            idm_interval[INTERVAL_ID_FIELD] = reading[INTERVAL_ID_FIELD]
            idm_interval[INTERVAL_START_FIELD] = reading[INTERVAL_START_FIELD]


def main_loop():
    """Loop and process messages from rtlamr."""
    idm_intervals = {}
    mqttc.loop_start()
    while True:
        try:
            amr_line = rtlamr.stdout.readline().strip()
            amr_dict = json.loads(amr_line)

            # Must have `message` or we ignore
            if "Message" not in amr_dict:
                continue

            amr_message = amr_dict["Message"]
            amr_time = parser.parse(amr_dict["Time"])
            fields_count = len(amr_message.values())

            # IDM results have 17 fields
            if fields_count == 17:
                msg_type = "idm"
                meter_id = str(amr_message[IDM_ID_FIELD])
                if meter_id not in idm_intervals:
                    idm_intervals[meter_id] = {}
                adjust_reading(
                    reading_time=amr_time,
                    meter_id=meter_id,
                    reading=amr_message,
                    consumption_field=IDM_CONSUMPTION_FIELD,
                    idm_interval=idm_intervals[meter_id],
                )

            # NetIDM results have 16 fields
            elif fields_count == 16:
                msg_type = "netidm"
                meter_id = str(amr_message[IDM_ID_FIELD])
                if meter_id not in idm_intervals:
                    idm_intervals[meter_id] = {}
                adjust_reading(
                    reading_time=amr_time,
                    meter_id=meter_id,
                    reading=amr_message,
                    consumption_field=NETIDM_CONSUMPTION_FIELD,
                    idm_interval=idm_intervals[meter_id],
                )

            # R900 results have 9 fields
            elif fields_count == 9:
                msg_type = "r900"
                meter_id = str(amr_message[ID_FIELD])
                adjust_reading(
                    reading_time=amr_time,
                    meter_id=meter_id,
                    reading=amr_message,
                    consumption_field=CONSUMPTION_FIELD,
                )

            # SCM results have 6 fields
            elif fields_count == 6:
                msg_type = "scm"
                meter_id = str(amr_message[ID_FIELD])
                adjust_reading(
                    reading_time=amr_time,
                    meter_id=meter_id,
                    reading=amr_message,
                    consumption_field=CONSUMPTION_FIELD,
                )

            # SCM+ results have 7 fields
            elif fields_count == 7:
                msg_type = "scm+"
                meter_id = str(amr_message[SCMPLUS_ID_FIELD])
                adjust_reading(
                    reading_time=amr_time,
                    meter_id=meter_id,
                    reading=amr_message,
                    consumption_field=CONSUMPTION_FIELD,
                )

            # invalid message or unsupported message type
            else:
                continue

            # Add last seen if in use
            if settings.LAST_SEEN_ENABLED:
                if settings.LAST_SEEN_FORMAT == "ISO_8601_local":
                    last_seen = (
                        datetime.now().replace(microsecond=0).astimezone().isoformat()
                    )
                elif settings.LAST_SEEN_FORMAT == "ISO_8601":
                    last_seen = (
                        datetime.utcnow()
                        .replace(microsecond=0, tzinfo=timezone.utc)
                        .isoformat()
                    )
                else:
                    last_seen = math.floor(time.time())

                amr_message["last_seen"] = last_seen

            # If in debugging mode, add the protocol to the message
            if settings.WATCHED_PROTOCOLS == "all":
                amr_message["Protocol"] = msg_type

            json_message = json.dumps(amr_message)
            logging.debug(
                "Meter: %s, MsgType: %s, Reading: %s",
                meter_id,
                msg_type,
                json_message,
            )

            # Don't publish messages for watched meters that are the wrong protocol
            # Seemed either some meters were dual protocool or two had duplicate IDs
            if (
                meter_id not in settings.METERS
                or msg_type == settings.METERS[meter_id]["protocol"]
            ):
                mqttc.publish(
                    topic=f"{settings.MQTT_BASE_TOPIC}/{meter_id}",
                    payload=json_message,
                )

        except Exception as ex:  # pylint: disable=broad-except
            logging.debug("Exception squashed! %s: %s", ex.__class__.__name__, ex)
            time.sleep(2)


# Register signals we listen for
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

rtlamr = start_rtlamr()
mqttc = create_mqtt_client()

if not settings.HA_DISCOVERY_DISABLED:
    send_discovery_messages()

main_loop()
