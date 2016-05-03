# coding=utf-8
from __future__ import absolute_import

import flask
import octoprint.plugin
import re
import RPi.GPIO as GPIO
import sys

class PowercontrolPlugin(octoprint.plugin.StartupPlugin,
			 octoprint.plugin.SettingsPlugin,
                         octoprint.plugin.AssetPlugin,
                         octoprint.plugin.TemplatePlugin,
			 octoprint.plugin.SimpleApiPlugin):

	##~~ Initialization

	def __init__(self):
		self.inOnePin = ""
		self.inTwoPin = ""
		self.isRaspi = False
		self.powerinfoActive = False
		self.printerRelay = ""
		self.relayOneName = ""
		self.relayTwoName = ""
		self.showPwrOneRelay = False
		self.showPwrTwoRelay = False

	##~~ StartupPlugin mixin

	def on_after_startup(self):
		# Try to find powerinfo plugin
		helpers = self._plugin_manager.get_helpers("powerinfo")
		self._logger.info("helpers %s" % helpers)
		if helpers and "isRaspi" in helpers:
		    self._logger.info("Using powerinfo as reference")
		    self.powerinfoActive = True
		    self.inOnePin = helpers["inOnePin"]
		    self.inTwoPin = helpers["inTwoPin"]
		    self.isRaspi = helpers["isRaspi"]
		    self.relayOneName = helpers["relayOneName"]
		    self.relayTwoName = helpers["relayTwoName"]
		    self.showPwrOneRelay = helpers["showPwrOneRelay"]
		    self.showPwrTwoRelay = helpers["showPwrTwoRelay"]
		else:
		    self._logger.info("Powerinfo not found or active, taking control!")
		    # No Powerinfo installed, get our own settings
		    self.inOnePin = int(self._settings.get(["inOnePin"]))
		    self.inTwoPin = int(self._settings.get(["inTwoPin"]))
		    self.relayOneName = self._settings.get(["rOneName"])
		    self.relayTwoName = self._settings.get(["rTwoName"])
		    self.showPwrOneRelay = self._settings.get(["showPwrOneRelay"])
		    self.showPwrTwoRelay = self._settings.get(["showPrwTwoRelay"])

		    if sys.platform == "linux2":
		    	with open('/proc/cpuinfo', 'r') as infile:
			    cpuinfo = infile.read()
		        # Search for the cpu info
		        match = re.search('Hardware\s+:\s+(\w+)$', cpuinfo, flags=re.MULTILINE | re.IGNORECASE)

		        if match is None:
			    # The hardware is not a pi
			    self.isRaspi = False
		    	elif match.group(1) == 'BCM2708':
			    self._logger.info("Pi 1")
			    self.isRaspi = True
		    	elif match.group(1) == 'BCM2709':
			    self._logger.info("Pi 2")
			    self.isRaspi = True
		    	elif match.group(1) == 'BCM2710':
			    self._logger.info("Pi 3")
			    self.isRaspi = True

		    	if self.isRaspi:
			    self._logger.info("Initialize GPIO")

			    if not self.powerinfoActive:
			    	# Set GPIO layout like pin-number
			    	GPIO.setmode(GPIO.BOARD)

			    	# Configure our GPIO outputs
                            	GPIO.setup(self.inOnePin, GPIO.OUT)
                            	GPIO.setup(self.inTwoPin, GPIO.OUT)

                            	# Setup the initial state to high(off)
                            	GPIO.output(self.inOnePin, GPIO.HIGH)
                            	GPIO.output(self.inTwoPin, GPIO.HIGH)

		self.printerRelay = int(self._settings.get(["printerRelay"]))

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			inOnePin="11",
			inTwoPin="12",
			printerRelay="1",
			relayOneName="Printer",
			relayTwoName="Light",
			showPwrOneRelay=True,
			showPwrTwoRelay=False 
		)

	def on_settings_save(self,data):
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

		# Try to find powerinfo plugin
                helpers = self._plugin_manager.get_helpers("powerinfo")

                if helpers and "isRaspi" in helpers:
                    self.isRaspi = helpers["isRaspi"]
                    self.powerinfoActive = True
                    self.inOnePin = helpers["inOnePin"]
                    self.inTwoPin = helpers["inTwoPin"]
                    self.relayOneName = helpers["relayOneName"]
                    self.relayTwoName = helpers["relayTwoName"]
		    self.showPwrOneRelay = helpers["showPwrOneRelay"]
		    self.showPwrTwoRelay = helpers["showPwrTwoRelay"]
		else:
		    self.powerinfoActive = False
		    self.inOnePin = int(self._settings.get["inOnePin"])
		    self.inTwoPin = int(self._settings.get["inTwoPin"])
                    self.relayOneName = self._settings.get(["rOneName"])
                    self.relayTwoName = self._settings.get(["rTwoName"])
		    self.showPwrOneRelay = self._settings.get(["showPwrOneRelay"])
		    self.showPwrTwoRelay = self._settings.get(["showPwrTwoRelay"])

		self.printerRelay = int(self._settings.get(["printerRelay"]))

		if not self.powerinfoActive:
                    # Set GPIO layout like pin-number
                    GPIO.setmode(GPIO.BOARD)

                    # Configure our GPIO outputs
                    GPIO.setup(self.inOnePin, GPIO.OUT)
                    GPIO.setup(self.inTwoPin, GPIO.OUT)

                    # Setup the initial state to high(off)
                    GPIO.output(self.inOnePin, GPIO.HIGH)
                    GPIO.output(self.inTwoPin, GPIO.HIGH)

	##~~ AssetPlugin mixin

	def get_assets(self):
		return dict(
			js=["js/powercontrol.js"]
		)

	##~~ TemplatePlugin mixin

        def get_template_configs(self):
            if self.isRaspi:
                return [
                        dict(type="sidebar", name="Powercontrol", custom_bindings=False),
                        dict(type="settings", name="Powercontrol", custom_bindings=False)
                ]
            else:
                return [
                ]

	##~~ SimpleApiPlugin mixin

	def on_api_get(self, request):
	    return flask.jsonify(dict(
                rOneName=self.relayOneName,
                rOneShow=self.showPwrOneRelay,
                rTwoName=self.relayTwoName,
                rTwoShow=self.showPwrTwoRelay,
		pRelay=self.printerRelay,
		pInfoActive=self.powerinfoActive
	    ))

	def get_api_commands(self):
	    return dict(pwrOnRelayOne=[],
			pwrOffRelayOne=[],
			pwrOnRelayTwo=[],
			pwrOffRelayTwo=[])

	def on_api_command(self, command, data):
	    if command == "pwrOnRelayOne":
		GPIO.output(self.inOnePin, GPIO.LOW)
		self.updatePlugin()
	    elif command == "pwrOffRelayOne":
		GPIO.output(self.inOnePin, GPIO.HIGH)
		self.updatePlugin()
	    elif command == "pwrOnRelayTwo":
		GPIO.output(self.inTwoPin, GPIO.LOW)
		self.updatePlugin()
	    elif command == "pwrOffRelayTwo":
		GPIO.output(self.inTwoPin, GPIO.HIGH)
		self.updatePlugin()

	def updatePlugin(self):
	    # Send our status update
	    self._plugin_manager.send_plugin_message(self._identifier, dict(rOneName=self.relayOneName,
                							    rOneShow=self.showPwrOneRelay,
                							    rTwoName=self.relayTwoName,
									    rTwoShow=self.showPwrTwoRelay,
									    pRelay=self.printerRelay,
									    pInfoActive=self.powerinfoActive))

	##~~ Softwareupdate hook

	def get_update_information(self):
		return dict(
			powercontrol=dict(
				displayName="Powercontrol Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="konvader",
				repo="OctoPrint-Powercontrol",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/konvader/OctoPrint-Relaycontrol/archive/{target_version}.zip"
			)
		)

__plugin_name__ = "Powercontrol Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PowercontrolPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
