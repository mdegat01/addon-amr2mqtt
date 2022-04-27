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

**Update:** I had a number of issues with the NooElec. Lots of others seem to have
success with it so maybe I got a bad one? It kept losing connection after a bit
and I had to unplug it and plug it back in to fix it. I switched to [this one][rtl-sdr-com-dongle]
from rtl-sdr.com and haven't had any issues since.

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

## MQTT Messages

This addon will publish a message to the topic `amr2mqtt/{meter_id}` each time
it receives a message if it is from a meter listed in `meters` (or if
`meters` is left blank). You can change `amr2mqtt` by setting `mqtt.base_topic`
(described below).

The content of those messages will be a JSON representation of what was received
from `rtlamr` except:

1. The current total consumption value will always be in `Consumption`. Some protocols
   use a different field so the add-on normalizes this.
1. The values in `Consumption` and (if present) `DifferentialConsumptionIntervals`
   will have been multiplied by the `multiplier` for that meter (if provided).

The addon will also publish [discovery messages][ha-mqtt-discovery] on start-up
to tell HA to create a device and various sensors for each meter you want to watch.
You can disable or customize this via options below.

## Finding Your Meter

Your meter should have an ID on it somewhere. It should be decent length integer,
mine was 8 digits. Mine was also on a sticker with a bar code, the big number
right below it. I don't know if yours will have the same location but it will be
on the device.

If you're having trouble finding it, set `meters` to `[]` in the config.
This will cause it to capture every message from every meter in range (regardless
of protocol) and pass them on to your MQTT broker. This way you can see them all
using a tool like [MQTT Explorer][mqtt-explorer] and find the ID that matches a
number you see on your device.

This is also a good way to figure out the protocol your meter is using if you're
not sure. When `meters` is left empty the add-on assumes you are debugging
and adds the protocol to every message.

You should not run long-term with `meters` left empty. Some protocols
require a lot of processing and you will be forcing the add-on to process a lot
messages. Once you have found your meter and figured out its protocol you should
add it to `meters` to reduce the overhead of this add-on.

**Note**: If you don't want to download additional software or do your debugging
via MQTT you can also set `log_level` to `debug` while `meters` is empty.
When `log_level` is set to `debug` then add-on will log each message it receives
along with the protocol and meter ID. This can get quite noisy though!

## Configuration

Example add-on configuration:

```yaml
meters:
  - id: 12345678
    protocol: scm
    name: My gas meter
    type: gas
    multiplier: 0.01
    unit_of_measurement: ccf
mqtt:
  host: 127.0.0.1
  port: 1883
```

**Note**: _This is just an example, don't copy and paste it! Create your own!_

### Option: `meters`

The list of meters you're tracking. `protocol` and `id` are required for each
meter. All other fields are optional and primarily used in discovery messages
to set up the Home Assistant entities.

#### Sub-option: `id`

ID of the meter, must be a positive integer.

#### Sub-option: `protocol`

Protocol the meter uses for its readings. Must be one of the following: `idm`,
`netidm`, `r900`, `scm`, or `scm+`.

#### Sub-option: `name`

Name for the meter. Only used in discovery messages.

#### Sub-option: `multiplier`

Meters can only report consumption in whole numbers and as a result they are
generally in an undesirable unit, like hundredsth of a kWh. Use this to convert
the consumption value reported by your meter to your preferred unit of measurement.

Examples:

- Consumption values in hundredsth of a kWh and you want kWh: set to `0.01`
- Consumption values in ccf and you want cubic meters: set to `2.83168466`

**Note:** If your meter uses `idm` or `netidm` then this multiplier will also be
used to convert the consumption value for each interval.

#### Sub-option: `precision`

Reported consumption values will be rounded to this many decimal places after the
multiplier is applied. If omitted, result will not be rounded.

#### Sub-option: `type`

Type of meter. must be one of the following: `gas`, `water`, or `energy`. Only
used in discovery messages.

#### Sub-option: `unit_of_measurement`

Unit of measurement for the consumption value. Only used in discovery messages.

#### Sub-option: `manufacturer`

Manufacturer of the meter. Only used in discovery messages.

#### Sub-option: `model`

Model of the meter. Only used in discovery messages.

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

By default, the topics of all MQTT messages begins with `amr2mqtt/{meter_ID}`.
If you set this option then the topics will begin with `{mqtt.base_topic}/{meter_id}`.

### Option: `last_seen`

Add `last_seen` field to each message with the current time in the specified format.
Options are: `ISO_8601`, `ISO_8601_local`, and `epoch`. Disabled if omitted. Useful
for detecting issues when meter normally reports in on a consistent interval.

### Option: `home_assistant_discovery_enabled`

Set to `false` to disable the add-on from sending discovery messages for the
watched meters.

### Option: `home_assistant_discovery_prefix`

Defaults to `homeassistant`. Set if you use a custom MQTT discovery prefix in
Home Assistant.

### Option: `rtlamr_symbol_length`

Sets symbollength in the rtlamr command used internally. If you are having issues
with high CPU usage, try lowering this number. Your goal should be to set it as
low as possible while still seeing results from your meter(s).

Valid values are: 8, 32, 40, 48, 56, 64, 72, 80, 88, 96. Default is 72. See [here][rtlamr-configuration]
for more information on rtlamr and this option.

## Home Assistant

If you enable discovery then on start-up this add-on will send MQTT messages telling
Home Assistant to make a device with the name you specified for each watched meter.
Then based on the type you specified for the meter it will send messages telling
Home Assistant to make a sensor for each expected attribute of readings from that
meter. Info on these can be found [here][rtlamr-protocols].

For most protocols only one sensor will be enabled by default, the current consumption
value. If your meter uses the `idm` or `netidm` protocol then there will be a second
enabled by default - the consumption value of the last interval. This sensor will
also have the consumption values of all intervals in an array in its `DifferentialConsumptionIntervals`
attribute. The sensors for all other attributes are disabled by default but you
can enable any you want to use.

## Troubleshooting

If you see the addon's log filling up with messages that look like this:

```txt
ll+, now 327
ll+, now 328
ll+, now 329
ll+, now 330
```

My understanding is that it means your hardware is underpowered for the task you're
asking it to do. R900 messages specifically seem to require a lot of work to process
and not all machines can keep up. See [here][reddit-ll-issue] for a full explanation.

If you are doing debug and discovery and have `meters` set to empty then
you can just ignore this. Just finish yoour debugging and then fill in `meters`
so it only processes messages in the protocol(s) you need. Hopefully it will go
away then.

If you are seeing this with `meters` filled in then you have an issue since
a meter you're trying to watch is using a protocol your machine can't handle.
Unfortunately I don't have a solution for you in this case, it seems like you won't
be able watch that meter. There are lots of communities for rtlamr as well as the
[github repo][github-rtlamr] so you may be able to come up with a solution. If
you do and it requires an enhancement to the addon feel free to submit an issue
with the info and I'll see what I can do.

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

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## License

MIT License

Copyright (c) 2021-2022 Mike Degatano

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
[forum]: https://community.home-assistant.io/t/home-assistant-add-on-amr2mqtt/378196
[github-rtlamr]: https://github.com/bemasher/rtlamr
[ha-mqtt-discovery]: https://www.home-assistant.io/docs/mqtt/discovery/#discovery-topic
[issue]: https://github.com/mdegat01/addon-amr2mqtt/issues
[mdegat01]: https://github.com/mdegat01
[mqtt-explorer]: https://mqtt-explorer.com/
[nesdr-nano-2plus]: https://www.amazon.com/NooElec-NESDR-Nano-Ultra-Low-Compatible/dp/B01B4L48QU
[ragingcomputer]: https://github.com/ragingcomputer
[reddit-ll-issue]: https://www.reddit.com/r/RTLSDR/comments/bjc4mk/tweakstips_for_reading_meters_with_rtlamr/em8vnwn/
[releases]: https://github.com/mdegat01/addon-amr2mqtt/releases
[rtl-sdr-com-dongle]: https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/
[rtl-sdr-dongle]: https://www.amazon.com/s?k=RTL2832U
[rtlamr-configuration]: https://github.com/bemasher/rtlamr/wiki/Configuration
[rtlamr-protocols]: https://github.com/bemasher/rtlamr/wiki/Protocol
[semver]: http://semver.org/spec/v2.0.0
