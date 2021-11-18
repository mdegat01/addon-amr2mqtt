#!/usr/bin/env python3
"""
Runs rtlamr to watch for broadcasts from power meter. If meter id
is in the list, usage is sent to 'readings/{meter id}/meter_reading'
topic on the MQTT broker specified in settings.

WATCHED_METERS = A Python list indicating those meter IDs to record and post.
MQTT_HOST = String containing the MQTT server address.
MQTT_PORT = An int containing the port the MQTT server is active on.

"""
import logging
import subprocess
import signal
import sys
import time
import paho.mqtt.client as mqtt
import settings


def shutdown(**_):
    """Disconnect MQTT client and send signal to shutdown and hard kill opened processes."""
    mqttc.disconnect()
    rtlamr.send_signal(15)
    time.sleep(1)
    rtlamr.send_signal(9)
    sys.exit(0)


def get_last_interval(meter_id):  # pylint: disable=redefined-outer-name
    """Get last interval."""
    return last_reading.get(meter_id, (None))


def set_last_interval(meter_id, interval_id):  # pylint: disable=redefined-outer-name
    """Set last interval."""
    last_reading[meter_id] = interval_id


# Register signals we listen for
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

# stores last interval id to avoid duplication, includes getter and setter
last_reading = {}

# Set up logging
logging.basicConfig()
logging.getLogger().setLevel(settings.LOG_LEVEL)

# start the rtlamr program.
rtlamr_cmd = [settings.RTLAMR, f"-msgtype={settings.MESSAGE_TYPES}", "-format=csv"]

# Add ID filter if we have a list of IDs to watch
if settings.WATCHED_METERS:
    rtlamr_cmd += [f"-filterid={settings.WATCHED_METERS}"]

rtlamr = subprocess.Popen(
    rtlamr_cmd,
    stdout=subprocess.PIPE,
    universal_newlines=True,
)

# Create MQTT client and add TLS and auth if necessary
mqttc = mqtt.Client(client_id=settings.MQTT_CLIENT_ID)

if settings.MQTT_CA_CERT:
    mqttc.tls_set(
        ca_certs=settings.MQTT_CA_CERT,
        certfile=settings.MQTT_CERTFILE,
        keyfile=settings.MQTT_KEYFILE,
    )

if settings.MQTT_USERNAME:
    mqttc.username_pw_set(
        settings.MQTT_USERNAME,
        password=settings.MQTT_PASSWORD,
    )

mqttc.connect(
    settings.MQTT_HOST,
    port=settings.MQTT_PORT,
    keepalive=60,
)

mqttc.loop_start()
while True:
    try:
        amrline = rtlamr.stdout.readline().strip()
        flds = amrline.split(",")
        interval_cur = None

        # proper IDM results have 66 fields
        if len(flds) == 66:
            # get some required info: meter ID, current meter reading,
            # current interval id, most recent interval usage
            meter_id = int(flds[9])

            read_cur = int(flds[15])
            interval_cur = int(flds[10])
            interval_read_cur = int(flds[16])

        # proper SCM results have 9 fields
        elif len(flds) == 9:
            # get some required info: meter ID, current meter reading,
            meter_id = int(flds[3])
            read_cur = int(flds[7])

        # invalid message or unsupported message type
        else:
            continue

        # Process interval if message type supports it (IDM)
        if interval_cur:
            # skip if interval is the same as last time we sent to MQTT
            if interval_cur == get_last_interval(meter_id):
                continue

            # as observed on on my meter...
            # using values set in settings...
            # each idm interval is 5 minutes (12x per hour),
            # measured in hundredths of a kilowatt hour
            # take the last interval usage times 10 to get watt-hours,
            # then times 12 to get average usage in watts
            rate = (
                interval_read_cur * settings.WH_MULTIPLIER * settings.READINGS_PER_HOUR
            )

            logging.debug("Sending meter %s rate: %s", meter_id, rate)
            mqttc.publish(
                f"{settings.MQTT_BASE_TOPIC}/{meter_id}/meter_rate",
                str(rate),
            )

            # store interval ID to avoid duplicating data
            set_last_interval(meter_id, interval_cur)

        # Send current reading to MQTT
        current_reading_in_kwh = (read_cur * settings.WH_MULTIPLIER) / 1000

        logging.debug("Sending meter %s reading: %s", meter_id, current_reading_in_kwh)
        mqttc.publish(
            f"{settings.MQTT_BASE_TOPIC}/{meter_id}/meter_reading",
            str(current_reading_in_kwh),
        )

    except Exception as ex:  # pylint: disable=broad-except
        logging.debug("Exception squashed! %s: %s", ex.__class__.__name__, ex)
        time.sleep(2)
