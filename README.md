# OctoPrint-Powercontrol

## Caution

You are playing around with mains voltage here. Mains can kill you!
Errors can be fatal, so if you do not know !exactly! what you are doing, you shouldn't be doing it!

## Description

Powercontrol is a plugin for OctoPi to control a 2 channel relay card (e.g. SainSmart).
You are able to configure input and output values for each relay within the settings. Changes will
take effect as soon as you click the Save button inside the OctoPrint Settings section. It is compatible
to all hardware revisions of Raspberry Pi including Pi3.

If you are using the Powerinfo plugin as well, Powercontrol will load and use the input and web-interface
configuration of Powerinfo automatically.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/konvader/OctoPrint-Powercontrol/archive/master.zip

## Configuration

 - Select input gpio pin for each relay (automatically done if Powerinfo is installed)
 - Define a custom label for each relay (automatically done if Powerinfo is installed)
 - Activate/Deactivate a 10 second warning before the relay is powered off
 - M117 gcode script support with custom messages for each relay
 - Cooldown delay up to 300 seconds before powering off the relay (if controlled over gcode)

Note: As we've initialized our GPIOs within the plugin (or Powerinfo), it is not necessary to do this anywhere else!
      Within the settings you have to use the pi's pin number not the GPIO number!
