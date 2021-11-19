# Home Assistant Add-on: AMR2MQTT

## Before You Begin

This add-on wants to collect consumption information being broadcast by the meter
on your house using an [RTL-SDR dongle][rtl-sdr-dongle] and pass it to MQTT. Which
means you'll need a dongle before you begin. I used a [NooElec NESDR Nano 2+][nesdr-nano-2plus]
but others work fine as well.

However note that this add-on does not work with all meters. Some potential problems
include:

- Meter does not broadcast consumption information, it just displays it
- Broadcasts by your meter are encrypted and cannot be used
- Meter only broadcasts once a month when the utility company pings it

So before beginning, check this list of [compatible meters][compatible-meters]
and see if your meter is on there. It will have the manufacturer and model number
printed on it somewhere.

This list isn't exhaustive so if you don't find your meter it may still work if
you're willing to take a gamble and order a dongle anyway. But just bear in mind
this solution is not universal and YMMV.

## Install

First add the repository to the add-on store (`https://github.com/mdegat01/hassio-addons`):

[![Open your Home Assistant instance and show the add add-on repository dialog
with a specific repository URL pre-filled.][add-repo-shield]][add-repo]

Then find AMR2MQTT in the store and click install:

[![Open your Home Assistant instance and show the dashboard of a Supervisor add-on.][add-addon-shield]][add-addon]

## MQTT Setup

This addon requires an MQTT broker. It will send the metrics it collects there
and expect clients like Home Assistant to read from that. By default it will use
the broker set up by the [Mosquitto addon][addon-mosquitto]. That add-on must be
installed and running prior to start-up. You generally don't need any additional
configuration for this, as long as that add-on is running this one will find and
use it.

[![Open your Home Assistant instance and show the dashboard of a Supervisor add-on.][add-addon-shield]][add-addon-mosquitto]

If you prefer to use your own MQTT broker, you must fill in the `mqtt` options
below.

This addon will publish messages to the topics `readings/{meter_id}/meter_reading`
and (IDM msgtype only) `readings/{meter_id}/interval_reading`. You can
customize this by setting `mqtt.base_topic` (described below).

## Finding Your Meter

Your meter should have an ID on it somewhere. It should be decent length integer,
mine was 8 digits. Mine was also on a sticker with a bar code, the big number
right below it. I don't know if yours will have the same location but it will be
on the device.

If you're having trouble finding it, add this to your config:

```yaml
watched_meters: []
msgtype:
  - scm
  - idm
log_level: debug
```

With this it will log every message from every meter in range (the log will get
quite noisy). Then you can match the meter IDs with what you see on your device.
This will also show you the message type so you can remove the type(s) your device
doesn't use.

Alternatively you can skip debug logging and use a tool like [MQTT Explorer][mqtt-explorer]
which lets you browse all available subtopics to see the IDs. Although you should
still figure out your message type via trial and error or debug logging and remove
the others from the list.

## Configuration

Example add-on configuration:

```yaml
watched_meters: []
msgtype:
  - idm
reading_multiplier: 0.01
mqtt:
  host: 127.0.0.1
  port: 1883
```

**Note**: _This is just an example, don't copy and paste it! Create your own!_

### Option: `watched_meters`

The list of meter IDs you're tracking. Must be integers. See above for instructions
on finding yours. Set to an empty array to listen for all meters in range.

### Option: `reading_multiplier`

Used to convert the consumption number to the unit of your choice. Consumption
numbers are whole numbers only so they may be in a weird unit, like hundredths
of a kWh. Readings will be multiplied by this number before being reported to
MQTT so you can convert to the unit you actually see on your bill.

### Option: `message_types`

Message type(s) your meter(s) use, will not read and process others. Supported options
are `idm`, `r900`, `scm`, and `scm+`.

### Option: `mqtt.host`

IP address or domain where your MQTT broker can be reached. Ex. `core-mosquitto`
or `127.0.0.1`

### Option: `mqtt.port`

Port your broker is listening on. Ex. `1883`

### Option: `mqtt.ca`

The CA certificate used to sign MQTT broker's certificate if broker is using a
self-signed certificate for TLS.

**Note**: _The file MUST be stored in `/ssl/`_

### Option: `mqtt.cert`

The absolute path to a certificate for client-authentication if MQTT broker is
using mTLS to authenticate clients.

### Option: `mqtt.key`

The absolute path to the key for the client-authentication certificate if MQTT
broker is using mTLS to authenticate clients.

**Note**: _This field is required if `client.certfile` is provided_

### Option: `mqtt.username`

Username to use when authenticating with MQTT broker.

### Option: `mqtt.password`

Password to use when authenticating with MQTT broker.

### Option: `mqtt.client_id`

Client ID to use when connecting to the MQTT broker.

### Option: `mqtt.base_topic`

By default, the topics of all MQTT messages begins with `readings/{meter_ID}`.
If you set this option then the topics will begin with `{mqtt.base_topic}/readings/{meter_id}`.

## Changelog & Releases

This repository keeps a change log using [GitHub's releases][releases]
functionality.

Releases are based on [Semantic Versioning][semver], and use the format
of `MAJOR.MINOR.PATCH`. In a nutshell, the version will be incremented
based on the following:

- `MAJOR`: Incompatible or major changes.
- `MINOR`: Backwards-compatible new features and enhancements.
- `PATCH`: Backwards-compatible bugfixes and package updates.

## Support

Got questions?

You have several ways to get them answered:

- The Home Assistant [Community Forum][forum]. I am
  [CentralCommand][forum-centralcommand] there.
- The Home Assistant [Discord Chat Server][discord-ha]. Use the #add-ons channel,
  I am CentralCommand#0913 there.

You could also [open an issue here][issue] on GitHub.

## Authors & contributors

The original setup of this repository is by [Mike Degatano][mdegat01].

The amridm2mqtt service this was built off of was created by [ragingcomputer][ragingcomputer].

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## License

MIT License

Copyright (c) 2021 mdegat01

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[add-addon-shield]: https://my.home-assistant.io/badges/supervisor_addon.svg
[add-addon]: https://my.home-assistant.io/redirect/supervisor_addon/?addon=39bd2704_amr2mqtt
[add-addon-mosquitto]: https://my.home-assistant.io/redirect/supervisor_addon/?addon=core_mosquitto
[add-repo-shield]: https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg
[add-repo]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fmdegat01%2Fhassio-addons
[addon-mosquitto]: https://github.com/home-assistant/addons/tree/master/mosquitto
[compatible-meters]: https://github.com/bemasher/rtlamr/wiki/Compatible-Meters
[contributors]: https://github.com/mdegat01/addon-amr2mqtt/graphs/contributors
[discord-ha]: https://discord.gg/c5DvZ4e
[forum-centralcommand]: https://community.home-assistant.io/u/CentralCommand/?u=CentralCommand
[forum]: https://community.home-assistant.io
[issue]: https://github.com/mdegat01/addon-amr2mqtt/issues
[mdegat01]: https://github.com/mdegat01
[mqtt-explorer]: https://mqtt-explorer.com/
[nesdr-nano-2plus]: https://www.amazon.com/NooElec-NESDR-Nano-Ultra-Low-Compatible/dp/B01B4L48QU
[ragingcomputer]: https://github.com/ragingcomputer
[releases]: https://github.com/mdegat01/addon-amr2mqtt/releases
[rtl-sdr-dongle]: https://www.amazon.com/s?k=RTL2832U
[semver]: http://semver.org/spec/v2.0.0
