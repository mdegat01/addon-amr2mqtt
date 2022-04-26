"""Get our settings from os.environ to facilitate running in Docker.
"""
import os
import logging
import json
import functools


def make_meters_map(meters, meter):
    """Add meter to meters by its ID."""
    meters[str(meter["id"])] = meter
    del meter["id"]
    return meters


# Pull in watched meters data
# If not empty, pull out IDs/protocols to watch
# If empty then we're in discovery mode
with open("/data/options.json", encoding="utf-8") as config_options:
    meters_config = json.load(config_options)["meters"]

if bool(meters_config):
    METERS = functools.reduce(make_meters_map, meters_config, {})
    WATCHED_METERS = ",".join(METERS.keys())
    WATCHED_PROTOCOLS = ",".join(set([meter["protocol"] for meter in meters_config]))
else:
    METERS = {}
    WATCHED_PROTOCOLS = "all"

# Get server, TLS and auth settings
MQTT_HOST = os.environ.get("MQTT_HOST")
MQTT_PORT = int(os.environ.get("MQTT_PORT"))
MQTT_CA_CERT = os.environ.get("MQTT_CA")
MQTT_CERTFILE = os.environ.get("MQTT_CERT")
MQTT_KEYFILE = os.environ.get("MQTT_KEY")
MQTT_USERNAME = os.environ.get("MQTT_USERNAME")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")
MQTT_CLIENT_ID = os.environ.get("MQTT_CLIENT_ID")

# Get discovery info
VIA_DEVICE = os.environ.get("BUILD_NAME")
SW_VERSION = os.environ.get("BUILD_VERSION")
HA_DISCOVERY_DISABLED = bool(os.environ.get("HA_DISCOVERY_DISABLED"))
discovery_topic = os.environ.get("HA_DISCOVERY_TOPIC")
HA_DISCOVERY_TOPIC = discovery_topic if bool(discovery_topic) else "homeassistant"

# Set the MQTT base topic
base_topic = os.environ.get("MQTT_BASE_TOPIC")
MQTT_BASE_TOPIC = base_topic if bool(base_topic) else "amr2mqtt"
MQTT_AVAILABILTY_TOPIC = f"{MQTT_BASE_TOPIC}/bridge/state"

# Using last seen
LAST_SEEN_FORMAT = os.environ.get("LAST_SEEN")
LAST_SEEN_ENABLED = LAST_SEEN_FORMAT != "disable"

# RTLAMR options
symbol_length = os.environ.get("SYMBOL_LENGTH")
SYMBOL_LENGTH = int(symbol_length) if bool(symbol_length) else 72

# Set up logging
EV_TO_LOG_LEVEL = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
log_level = EV_TO_LOG_LEVEL.get(os.environ.get("LOG_LEVEL"))
logging.basicConfig()
logging.getLogger().setLevel(log_level)

# path to rtlamr
RTLAMR = "/usr/bin/rtlamr"
