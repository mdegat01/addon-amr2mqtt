# Home Assistant Add-on: HedgeDoc

## Install

First add the repository to the add-on store (`https://github.com/mdegat01/hassio-addons`):

[![Open your Home Assistant instance and show the add add-on repository dialog
with a specific repository URL pre-filled.][add-repo-shield]][add-repo]

Then find HedgeDoc in the store and click install:

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
below. Please note there is no easy upgrade path between these two options.

This addon will publish messages to the topics `readings/{meter_id}/meter_reading`
and `readings/{meter_id}/meter_rate`. You can customize this by setting `mqtt.base_topic`
below.

## RTL-SDR Dongle Setup

TODO

## Configuration

Example add-on configuration:

```
TODO
```

**Note**: _This is just an example, don't copy and paste it! Create your own!_

### Option: `watched_meters`

TODO

### Option: `wh_multiplier`

TODO

### Option: `readings_per_hour`

TODO

### Option: `mqtt.host`

TODO

### Option: `mqtt.ca`

TODO

**Note**: _The file MUST be stored in `/ssl/`_

### Option: `mqtt.cert`

TODO

**Note**: _The file MUST be stored in `/ssl/`_

### Option: `mqtt.key`

TODO

**Note**: _The file MUST be stored in `/ssl/`_

### Option: `mqtt.username`

TODO

### Option: `mqtt.password`

TODO

### Option: `mqtt.client_id`

TODO

### Option: `mqtt.base_topic`

TODO

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

The amridm2mqtt service ported here was created by [ragingcomputer][ragingcomputer].

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
[add-addon]: https://my.home-assistant.io/redirect/supervisor_addon/?addon=39bd2704_amridm2mqtt
[add-addon-mosquitto]: https://my.home-assistant.io/redirect/supervisor_addon/?addon=core_mosquitto
[add-repo-shield]: https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg
[add-repo]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fmdegat01%2Fhassio-addons
[addon-mosquitto]: https://github.com/home-assistant/addons/tree/master/mosquitto
[amridm2mqtt]: https://github.com/ragingcomputer/amridm2mqtt
[contributors]: https://github.com/mdegat01/addon-hedgedoc/graphs/contributors
[discord-ha]: https://discord.gg/c5DvZ4e
[forum-centralcommand]: https://community.home-assistant.io/u/CentralCommand/?u=CentralCommand
[forum]: https://community.home-assistant.io/t/home-assistant-add-on-hedgedoc/296809?u=CentralCommand
[issue]: https://github.com/mdegat01/addon-hedgedoc/issues
[mdegat01]: https://github.com/mdegat01
[ragingcomputer]: https://github.com/ragingcomputer
[releases]: https://github.com/mdegat01/addon-hedgedoc/releases
[semver]: http://semver.org/spec/v2.0.0
