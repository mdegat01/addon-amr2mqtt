"""Get our settings from os.environ to facilitate running in Docker.
"""
import os
import logging

# List of the Meter IDs to watch
# Use empty brackets to read all meters - []
# List may contain only one entry - [12345678]
# or multiple entries - [12345678, 98765432, 12340123]
power_meters = os.environ["WATCHED_METERS"].replace(",", " ").split(" ")
WATCHED_METERS = [int(meter_id) for meter_id in power_meters if meter_id]

# multiplier to get reading to Watt Hours (Wh)
# examples:
#   for meter providing readings in kWh
#      MULTIPLIER = 1000
#   for meter providing readings in kWh
#   with 2 extra digits of precision
#      MULTIPLIER = 10
# MULTIPLIER needs to be a number
WH_MULTIPLIER = int(os.environ.get("WH_MULTIPLIER", 1000))

# number of IDM intervals per hour reported by the meter
# examples:
#   for meter providing readings every 5 minutes
#   or 12 times every hour
#     READINGS_PER_HOUR = 12
#   for meter providing readings every 15 minutes
#   or 12 times every hour
#     READINGS_PER_HOUR = 4
READINGS_PER_HOUR = int(os.environ.get("READINGS_PER_HOUR", 12))

# MQTT Server settings
# MQTT_HOST needs to be a string
# MQTT_PORT needs to be an int
# MQTT_USER needs to be a string
# MQTT_PASSWORD needs to be a string
# MQTT_CLIENT_ID is a string if provided, library randomly generates one if omitted
# If no authentication, leave MQTT_USER and MQTT_PASSWORD empty
MQTT_HOST = os.environ.get("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_USER = os.environ.get("MQTT_USER", "")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "")
MQTT_CLIENT_ID = os.environ.get("MQTT_CLIENT_ID")

# If TLS in use, a CA file must be provided
# Client Key+Cert can optionally be provided as well
if os.environ.get("MQTT_CA"):
    MQTT_TLS = {
        "ca_certs": os.environ.get("MQTT_CA"),
        "certfile": os.environ.get("MQTT_CERT"),
        "keyfile": os.environ.get("MQTT_KEY"),
    }
else:
    MQTT_TLS = None

# Set the MQTT base topic with the user's prefix if provided
MQTT_DEFAULT_BASE_TOPIC = "readings"
if os.environ.get("MQTT_BASE_TOPIC"):
    MQTT_BASE_TOPIC = f'${os.environ.get("MQTT_BASE_TOPIC")}/${MQTT_DEFAULT_BASE_TOPIC}'
else:
    MQTT_BASE_TOPIC = MQTT_DEFAULT_BASE_TOPIC

# Set logging level
EV_TO_LOG_LEVEL = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
LOG_LEVEL = EV_TO_LOG_LEVEL.get(os.environ.get("LOG_LEVEL"))

# path to rtlamr
RTLAMR = "/usr/bin/rtlamr"

# path to rtl_tcp
RTL_TCP = "/usr/bin/rtl_tcp"
