# OctoPrint-Powercontrol

## Caution

You are playing around with mains voltage here. Mains can kill you!
Errors can be fatal, so if you do not know !exactly! what you are doing, you shouldn't be doing it!

## Description

Powercontrol is a plugin for OctoPi to control a 2 channel relay card (e.g. SainSmart).
You are able to configure input and output values for each relay within the settings. Changes will
take effect as soon as you click the Save button inside the OctoPrint Settings section. It is compatible
to all hardware revisions of Raspberry Pi including Pi3.

If you are using the Powerinfo plugin as well, Powercontrol will load and use the input configuration of
Powerinfo automatically.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/konvader/OctoPrint-Powercontrol/archive/master.zip

Note: As we've initialized our GPIOs within the plugin, it is not necessary to do this anywhere else!
      Within the settings you have to use the pi's pin number not the GPIO number!
