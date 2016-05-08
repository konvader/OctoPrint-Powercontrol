# coding=utf-8
from __future__ import absolute_import

from octoprint.util import RepeatedTimer
from octoprint.events import Events
import flask
import octoprint.plugin
import re
import RPi.GPIO as GPIO
import sys

class PowercontrolPlugin(octoprint.plugin.StartupPlugin,
			 octoprint.plugin.SettingsPlugin,
                         octoprint.plugin.AssetPlugin,
			 octoprint.plugin.EventHandlerPlugin,
                         octoprint.plugin.TemplatePlugin,
			 octoprint.plugin.SimpleApiPlugin,
			 octoprint.plugin.OctoPrintPlugin):

	##~~ Initialization

	def __init__(self):
		self._cooldownOneTimeoutValue = None
		self._cooldownOneTimer = None
		self._cooldownTwoTimeoutValue = None
		self._cooldownTwoTimer = None
		self._helperWaitTimeoutValue = 1
		self._helperWaitTimer = None
		self._pwrOneTimeoutValue = None
                self._pwrOneTimer = None
		self._pwrTwoTimeoutValue = None
		self._pwrTwoTimer = None
		self.cooldownDelay = ""
		self.inOnePin = ""
		self.inTwoPin = ""
		self.isRaspi = False
		self.onOneMessage = ""
		self.offOneMessage = ""
		self.onTwoMessage = ""
		self.offTwoMessage = ""
		self.powerinfoActive = False
		self.pwrMessage = ""
		self.relayOneName = ""
		self.relayOneCooldownEnabled = False
		self.relayTwoName = ""
		self.relayTwoCooldownEnabled = False
		self.showPwrOneRelay = False
		self.showPwrTwoRelay = False
		self.warnOnPwrOffRelayOne = False
		self.warnOnPwrOffRelayTwo = False

	##~~ StartupPlugin mixin

	def on_after_startup(self):
		if sys.platform == "linux2":
		    with open('/proc/cpuinfo', 'r') as infile:
			cpuinfo = infile.read()
		    # Search for the cpu info
		    match = re.search('Hardware\s+:\s+(\w+)$', cpuinfo, flags=re.MULTILINE | re.IGNORECASE)

		    if match is None:
			# The hardware is not a pi
			self.isRaspi = False
		    elif match.group(1) == 'BCM2708':
			self._logger.debug("Pi 1")
			self.isRaspi = True
		    elif match.group(1) == 'BCM2709':
			self._logger.debug("Pi 2")
			self.isRaspi = True
		    elif match.group(1) == 'BCM2710':
			self._logger.debug("Pi 3")
			self.isRaspi = True

		self.cooldownDelay = int(self._settings.get(["cooldownDelay"]))
                self.inOnePin = int(self._settings.get(["inOnePin"]))
                self.inTwoPin = int(self._settings.get(["inTwoPin"]))
		self.onOneMessage = self._settings.get(["onOneMessage"])
		self.offOneMessage = self._settings.get(["offOneMessage"])
		self.onTwoMessage = self._settings.get(["onTwoMessage"])
		self.offTwoMessage = self._settings.get(["offTwoMessage"])
		self._settings.set(["powerinfoActive"], self.powerinfoActive)
                self.relayOneName = self._settings.get(["relayOneName"])
		self.relayOneCooldownEnabled = self._settings.get(["relayOneCooldownEnabled"])
                self.relayTwoName = self._settings.get(["relayTwoName"])
		self.relayTwoCooldownEnabled = self._settings.get(["relayTwoCooldownEnabled"])
                self.showPwrOneRelay = self._settings.get(["showPwrOneRelay"])
                self.showPwrTwoRelay = self._settings.get(["showPwrTwoRelay"])
		self.warnOnPwrOffRelayOne = self._settings.get(["warnOnPwrOffRelayOne"])
		self.warnOnPwrOffRelayTwo = self._settings.get(["warnOnPwrOffRelayTwo"])
		self.updatePlugin()
		
		self._helperWaitTimer = RepeatedTimer(1, self._helper_wait_task)
                self._helperWaitTimer.start()

	def _helper_wait_task(self):
		self._helperWaitTimeoutValue -= 1
            	if self._helperWaitTimeoutValue <= 0:
                	self._helperWaitTimer.cancel()
                	self._helperWaitTimer = None
			self.get_helpers()

	def get_helpers(self):
		# Try to find powerinfo plugin
                helpers = self._plugin_manager.get_helpers("powerinfo")
                self._logger.info("helpers %s" % helpers)
                if helpers and "inOnePin" in helpers:
                    self.powerinfoActive = True
		    self._settings.set(["powerinfoActive"], self.powerinfoActive)
                    self._logger.debug("Using powerinfo as reference")
                    self.inOnePin = helpers["inOnePin"]
                    self.inTwoPin = helpers["inTwoPin"]
                    self.relayOneName = helpers["relayOneName"]
                    self.relayTwoName = helpers["relayTwoName"]
                    self.showPwrOneRelay = helpers["showPwrOneRelay"]
                    self.showPwrTwoRelay = helpers["showPwrTwoRelay"]

		if self.isRaspi and not self.powerinfoActive:
		    self._logger.debug("Powercontrol: Initialize GPIO")
		    # Set GPIO layout like pin-number
		    GPIO.setmode(GPIO.BOARD)

		    # Configure our GPIO outputs
                    GPIO.setup(self.inOnePin, GPIO.OUT)
                    GPIO.setup(self.inTwoPin, GPIO.OUT)

                    # Setup the initial state to high(off)
                    GPIO.output(self.inOnePin, GPIO.HIGH)
                    GPIO.output(self.inTwoPin, GPIO.HIGH)

		self.updatePlugin()

	##~~ OctoPrintPlugin hook

	def hook_m117(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
	    if gcode and gcode == "M117":
		self._logger.info("Got message: {0}".format(cmd))
		self.pwrMessage = cmd[5:]
		if self.pwrMessage == self.onOneMessage:
		    GPIO.output(self.inOnePin, GPIO.LOW)
		elif self.pwrMessage == self.offOneMessage:
		    if self.relayOneCooldownEnabled:
                        self._cooldownOneTimeoutValue = self.cooldownDelay
                        self._cooldownOneTimer = RepeatedTimer(1, self._cooldownOne_task)
                        self._cooldownOneTimer.start()
                        self._plugin_manager.send_plugin_message(self._identifier, dict(type="cooldownOne", timeout_value=self._cooldownOneTimeoutValue))
                    else:
                        GPIO.output(self.inOnePin, GPIO.HIGH)
		elif self.pwrMessage == self.onTwoMessage:
		    GPIO.output(self.inTwoPin, GPIO.LOW)
		elif self.pwrMessage == self.offTwoMessage:
		    if self.relayTwoCooldownEnabled:
                        self._cooldownTwoTimeoutValue = self.cooldownDelay
                        self._cooldownTwoTimer = RepeatedTimer(1, self._cooldownTwo_task)
                        self._cooldownTwoTimer.start()
                        self._plugin_manager.send_plugin_message(self._identifier, dict(type="cooldownTwo", timeout_value=self._cooldownTwoTimeoutValue))
                    else:
                        GPIO.output(self.inTwoPin, GPIO.HIGH)

	def _cooldownOne_task(self):
            self._cooldownOneTimeoutValue -= 1
            self._plugin_manager.send_plugin_message(self._identifier, dict(type="cooldownOne", timeout_value=self._cooldownOneTimeoutValue))
            if self._cooldownOneTimeoutValue <= 0:
                self._cooldownOneTimer.cancel()
                self._cooldownOneTimer = None
                GPIO.output(self.inOnePin, GPIO.HIGH)
                self.updatePlugin()

	def _cooldownTwo_task(self):
            self._cooldownTwoTimeoutValue -= 1
            self._plugin_manager.send_plugin_message(self._identifier, dict(type="cooldownTwo", timeout_value=self._cooldownTwoTimeoutValue))
            if self._cooldownTwoTimeoutValue <= 0:
                self._cooldownTwoTimer.cancel()
                self._cooldownTwoTimer = None
                GPIO.output(self.inTwoPin, GPIO.HIGH)
                self.updatePlugin()

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			cooldownDelay="120",
			inOnePin="11",
			inTwoPin="12",
			onOneMessage="Printer on",
			offOneMessage="Printer off",
			onTwoMessage="Light on",
			offTwoMessage="Light off",
			powerinfoActive=False,
			relayOneName="Printer",
			relayOneCooldownEnabled=True,
			relayTwoName="Light",
			relayTwoCooldownEnabled=False,
			showPwrOneRelay=True,
			showPwrTwoRelay=False,
			warnOnPwrOffRelayOne=True,
			warnOnPwrOffRelayTwo=True
		)

	def on_settings_save(self, data):
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

		self.cooldownDelay = int(self._settings.get(["cooldownDelay"]))
		self.inOnePin = int(self._settings.get(["inOnePin"]))
		self.inTwoPin = int(self._settings.get(["inTwoPin"]))
		self.onOneMessage = self._settings.get(["onOneMessage"])
		self.offOneMessage = self._settings.get(["offOneMessage"])
		self.onTwoMessage = self._settings.get(["onTwoMessage"])
		self.offTwoMessage = self._settings.get(["offTwoMessage"])
		self.relayOneName = self._settings.get(["relayOneName"])
		self.relayOneCooldownEnabled = self._settings.get(["relayOneCooldownEnabled"])
		self.relayTwoName = self._settings.get(["relayTwoName"])
		self.relayTwoCooldownEnabled = self._settings.get(["relayTwoCooldownEnabled"])
		self.showPwrOneRelay = self._settings.get(["showPwrOneRelay"])
		self.showPwrTwoRelay = self._settings.get(["showPwrTwoRelay"])
		self.warnOnPwrOffRelayOne = self._settings.get(["warnOnPwrOffRelayOne"])
		self.warnOnPwrOffRelayTwo = self._settings.get(["warnOnPwrOffRelayTwo"])
		self.updatePlugin()

		self._helperWaitTimeoutValue = 1
		self._helperWaitTimer = RepeatedTimer(1, self._helper_wait_task)
		self._helperWaitTimer.start()

	##~~ AssetPlugin mixin

	def get_assets(self):
		return dict(
			js=["js/powercontrol.js"]
		)

	##~~ TemplatePlugin mixin

        def get_template_configs(self):
            if self.isRaspi:
                return [
                        dict(type="sidebar", name="Powercontrol"),
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
                rTwoShow=self.showPwrTwoRelay
	    ))

	def get_api_commands(self):
	    return dict(pwrOnRelayOne=[],
			pwrOffRelayOne=[],
			pwrOnRelayTwo=[],
			pwrOffRelayTwo=[],
			cancelOne=[],
			cancelCooldownOne=[],
			cancelTwo=[],
			cancelCooldownTwo=[])

	def on_api_command(self, command, data):
	    if command == "pwrOnRelayOne":
		GPIO.output(self.inOnePin, GPIO.LOW)
		self.updatePlugin()
	    elif command == "pwrOffRelayOne":
		if self.warnOnPwrOffRelayOne:
		    self._pwrOneTimeoutValue = 10
                    self._pwrOneTimer = RepeatedTimer(1, self._timerOne_task)
                    self._pwrOneTimer.start()
                    self._plugin_manager.send_plugin_message(self._identifier, dict(type="timeoutOne", timeout_value=self._pwrOneTimeoutValue))
		else:
		    GPIO.output(self.inOnePin, GPIO.HIGH)
		    self.updatePlugin()
	    elif command == "pwrOnRelayTwo":
		GPIO.output(self.inTwoPin, GPIO.LOW)
		self.updatePlugin()
	    elif command == "pwrOffRelayTwo":
		if self.warnOnPwrOffRelayTwo:
		    self._pwrTwoTimeoutValue = 10
                    self._pwrTwoTimer = RepeatedTimer(1, self._timerTwo_task)
                    self._pwrTwoTimer.start()
                    self._plugin_manager.send_plugin_message(self._identifier, dict(type="timeoutTwo", timeout_value=self._pwrTwoTimeoutValue))
		else:
		    GPIO.output(self.inTwoPin, GPIO.HIGH)
		    self.updatePlugin()
	    elif command == "cancelOne":
		self._pwrOneTimer.cancel()
		self._logger.info("Cancelled power off relay 1.")
	    elif command == "cancelCooldownOne":
                self._cooldownOneTimer.cancel()
                self._logger.info("Cancelled cooldown power off relay 1.")
	    elif command == "cancelTwo":
		self._pwrTwoTimer.cancel()
		self._logger.info("Cancelled power off relay 2.")
	    elif command == "cancelCooldownTwo":
                self._cooldownTwoTimer.cancel()
                self._logger.info("Cancelled cooldown power off relay 2.")

	def _timerOne_task(self):
	    self._pwrOneTimeoutValue -= 1
	    self._plugin_manager.send_plugin_message(self._identifier, dict(type="timeoutOne", timeout_value=self._pwrOneTimeoutValue))
	    if self._pwrOneTimeoutValue <= 0:
		self._pwrOneTimer.cancel()
		self._pwrOneTimer = None
		GPIO.output(self.inOnePin, GPIO.HIGH)
		self.updatePlugin()

	def _timerTwo_task(self):
	    self._pwrTwoTimeoutValue -= 1
	    self._plugin_manager.send_plugin_message(self._identifier, dict(type="timeoutTwo", timeout_value=self._pwrTwoTimeoutValue))
	    if self._pwrTwoTimeoutValue <= 0:
		self._pwrTwoTimer.cancel()
		self._pwrTwoTimer = None
		GPIO.output(self.inTwoPin, GPIO.HIGH)
		self.updatePlugin()

	def updatePlugin(self):
	    # Send our status update
	    self._plugin_manager.send_plugin_message(self._identifier, dict(rOneName=self.relayOneName,
                							    rOneShow=self.showPwrOneRelay,
                							    rTwoName=self.relayTwoName,
									    rTwoShow=self.showPwrTwoRelay))

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
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
		"octoprint.comm.protocol.gcode.sent": __plugin_implementation__.hook_m117
	}
