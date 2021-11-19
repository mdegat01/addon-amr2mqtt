"""Get our settings from os.environ to facilitate running in Docker.
"""
import os
import logging

# List of the Meter IDs to watch
# Use empty string to read all meters
# List may contain only one entry - "12345678"
# or multiple entries - "12345678,98765432,12340123"
WATCHED_METERS = os.environ["WATCHED_METERS"]

# List of message types to watch for
# Must be provided as only specific types are supported right now
# See differences here: https://github.com/bemasher/rtlamr#message-types
MESSAGE_TYPES = os.environ["MESSAGE_TYPES"]

# If in discovery mode we simply log everything at debug level
DISCOVERY_MODE = MESSAGE_TYPES == "all"

# Normally we want CSV but discovery mode lets people pick
MESSAGE_FORMAT = os.environ["DISCOVERY_FORMAT"] if DISCOVERY_MODE else "csv"

# multiplier to get reading to desired units
# examples:
#   for meter providing readings in desired units currently
#      MULTIPLIER = 1
#   for meter providing readings with 2 extra digits of precision
#        Ex. Hundreds of a kWh instead of just kWh
#      MULTIPLIER = 0.01
# MULTIPLIER needs to be a number
READING_MULTIPLIER = float(os.environ.get("READING_MULTIPLIER"))

# Get server, TLS and auth settings
MQTT_HOST = os.environ.get("MQTT_HOST")
MQTT_PORT = int(os.environ.get("MQTT_PORT"))
MQTT_CA_CERT = os.environ.get("MQTT_CA")
MQTT_CERTFILE = os.environ.get("MQTT_CERT")
MQTT_KEYFILE = os.environ.get("MQTT_KEY")
MQTT_USERNAME = os.environ.get("MQTT_USERNAME")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")
MQTT_CLIENT_ID = os.environ.get("MQTT_CLIENT_ID")

# Set the MQTT base topic with the user's prefix if provided
MQTT_DEFAULT_BASE_TOPIC = "readings"
if os.environ.get("MQTT_BASE_TOPIC"):
    MQTT_BASE_TOPIC = f'{os.environ.get("MQTT_BASE_TOPIC")}/{MQTT_DEFAULT_BASE_TOPIC}'
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
