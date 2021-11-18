#!/usr/bin/with-contenv bashio
# shellcheck shell=bash
# ==============================================================================
# Home Assistant Add-on: AMR2MQTT
# This validates config and sets up app files/folders
# ==============================================================================

# -- CONFIG SUGGESTIONS/VALIDATIONS ---
bashio::log.debug "Validate config and look for suggestions"

if bashio::config.exists 'mqtt.ca'; then
    if ! bashio::fs.file_exists "/ssl/$(bashio::config 'mqtt.ca')"; then
        bashio::log.fatal
        bashio::log.fatal "The file specified for 'mqtt.ca' does not exist!"
        bashio::log.fatal "Ensure CA file exists in /ssl and correct path is provided."
        bashio::log.fatal
        bashio::exit.nok
    fi
else
    if bashio::config.exists 'mqtt.cert'; then
        bashio::log.fatal
        bashio::log.fatal "Client certificate provided but TLS isn't in use!"
        bashio::log.fatal "Please provide a CA certificate to enable TLS connection to your broker."
        bashio::log.fatal
        bashio::exit.nok
    fi
fi
if bashio::config.exists 'mqtt.cert'; then
    if ! bashio::fs.file_exists "$(bashio::config 'mqtt.cert')"; then
        bashio::log.fatal
        bashio::log.fatal "The file specified for 'mqtt.cert' does not exist!"
        bashio::log.fatal "Ensure client certificate file exists and full path is provided."
        bashio::log.fatal
        bashio::exit.nok
    fi
    if ! bashio::fs.file_exists "$(bashio::config 'mqtt.key')"; then
        bashio::log.fatal
        bashio::log.fatal "The file specified for 'mqtt.key' does not exist!"
        bashio::log.fatal "Ensure client certificate key file exists and full path is provided."
        bashio::log.fatal
        bashio::exit.nok
    fi
else
    if bashio::config.exists 'mqtt.key'; then
        bashio::log.warning "Invalid option: 'mqtt.key' set without 'mqtt.cert'. Removing..."
        bashio::addon.option 'mqtt.key'
    fi
fi