#!/usr/bin/env python3
"""
Runs rtlamr to watch for broadcasts from power meter(s). Passings readings
found to MQTT at topic `amr2mqtt/{meter_ID}`. If meter ID
is a watched one, processes its reading using settings first.

"""
import logging
import subprocess
import signal
import sys
import time
import json
import paho.mqtt.client as mqtt
import settings


def shutdown(**_):
    """Disconnect MQTT client and send signal to shutdown and hard kill opened processes."""
    mqttc.disconnect()
    rtlamr.send_signal(15)
    time.sleep(1)
    rtlamr.send_signal(9)
    sys.exit(0)


def adjust_reading(m_id, reading, consumption_field, interval_field=None):
    """Convert consumption and interval data using configured multiplier."""
    if m_id in settings.METERS:
        config = settings.METERS[m_id]
        multiplier = config.get("reading_multiplier", 1)
        reading["Consumption"] = reading[consumption_field] * multiplier

        if interval_field:
            reading["DifferentialConsumptionIntervals"] = [
                interval * multiplier for interval in reading[interval_field]
            ]


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

    return subprocess.Popen(
        rtlamr_cmd,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )


def create_mqtt_client():
    """Create MQTT client with TLS and auth if necessary."""
    client = mqtt.Client(client_id=settings.MQTT_CLIENT_ID)

    if settings.MQTT_CA_CERT:
        client.tls_set(
            ca_certs=settings.MQTT_CA_CERT,
            certfile=settings.MQTT_CERTFILE,
            keyfile=settings.MQTT_KEYFILE,
        )

    if settings.MQTT_USERNAME:
        client.username_pw_set(
            settings.MQTT_USERNAME,
            password=settings.MQTT_PASSWORD,
        )

    client.connect(
        settings.MQTT_HOST,
        port=settings.MQTT_PORT,
        keepalive=60,
    )
    return client


def main_loop():
    """Loop and process messages from rtlamr."""
    mqttc.loop_start()
    while True:
        try:
            amr_line = rtlamr.stdout.readline().strip()
            amr_dict = json.loads(amr_line)

            # Must have `message` or we ignore
            if "Message" not in amr_dict:
                continue

            amr_message = amr_dict["Message"]
            fields_count = len(amr_message.values())

            # IDM results have 17 fields
            if fields_count == 17:
                msg_type = "idm"
                meter_id = str(amr_message["ERTSerialNumber"])
                adjust_reading(
                    meter_id,
                    amr_message,
                    "LastConsumptionCount",
                    "DifferentialConsumptionIntervals",
                )

            # NetIDM results have 16 fields
            elif fields_count == 16:
                msg_type = "netidm"
                meter_id = str(amr_message["ERTSerialNumber"])
                adjust_reading(
                    meter_id,
                    amr_message,
                    "LastConsumptionNet",
                    "DifferentialConsumptionIntervals",
                )

            # R900 results have 9 fields
            elif fields_count == 9:
                msg_type = "r900"
                meter_id = str(amr_message["ID"])
                adjust_reading(meter_id, amr_message, "Consumption")

            # SCM results have 6 fields
            elif fields_count == 6:
                msg_type = "scm"
                meter_id = str(amr_message["ID"])
                adjust_reading(meter_id, amr_message, "Consumption")

            # SCM+ results have 7 fields
            elif fields_count == 7:
                msg_type = "scm+"
                meter_id = str(amr_message["EndpointID"])
                adjust_reading(meter_id, amr_message, "Consumption")

            # invalid message or unsupported message type
            else:
                continue

            json_message = json.dumps(amr_message)
            logging.debug(
                "Meter: %s, MsgType: %s, Reading: %s",
                meter_id,
                msg_type,
                json_message,
            )
            mqttc.publish(
                f"{settings.MQTT_BASE_TOPIC}/{meter_id}",
                json_message,
            )

        except Exception as ex:  # pylint: disable=broad-except
            logging.debug("Exception squashed! %s: %s", ex.__class__.__name__, ex)
            time.sleep(2)


# Register signals we listen for
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

rtlamr = start_rtlamr()
mqttc = create_mqtt_client()
main_loop()
