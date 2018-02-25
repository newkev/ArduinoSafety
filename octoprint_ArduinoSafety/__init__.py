# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin
import serial
import binascii
from threading import Thread
import time

from time import sleep

class HelloWorldPlugin(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin):
	def on_after_startup(self):
    		self._logger.info("Hello World!")
		conf = self.get_config_vars()
		self.comthread = SerialThread(self, conf)

	def get_settings_defaults(self):
	    return dict(
		comport="/dev/ttyUSB0",
		baudrate=9600,
		url="https://en.wikipedia.org/wiki/Hello_world"
		)

	def get_config_vars(self):
		return dict(
			comport=self._settings.get(["comport"]),
			baudrate=self._settings.get(["baudrate"])
		)

	def get_template_configs(self):
	    return [
        	dict(type="navbar", custom_bindings=False),
	        dict(type="settings", custom_bindings=False)
	    ]
	
	def getLogger(self):
		return self._logger

__plugin_name__ = "Arduino Safety"
__plugin_implementation__ = HelloWorldPlugin()

class SerialThread(Thread):
	# comport parameters
	portname = ""
	baudrate = 9600

	# thread parameters
	interrupted = False

	# msg parser vars
	msgParsingState = 0
	bytesRead = []
	payload = []
	countBytesRead = 0
	ackPending = False

	#	comport = "/dev/ttyUSB0",#
	# baudrate = 9600,

	def __init__(self, callbackClass, config):
		Thread.__init__(self)
		self.cbClass = callbackClass
		self.portname = config["comport"]
		self.baudrate = config["baudrate"]

		try:
			self.port = serial.Serial(self.portname, baudrate=self.baudrate, timeout=3.0)
			time.sleep(5)
			callbackClass.getLogger().info("Arduino Comthread started")
		except:
			self.interrupt()
			callbackClass.getLogger().error("Could not open comport to Arduino:" + self.portname)
	
		self.daemon = False
		self.start()

	def run(self):
		self.cbClass.getLogger().info("Thread started")

		while not self.interrupted:
			try:
				readl = self.port.readline()
				self.cbClass.getLogger().info(readl)
			except:
				pass
		self.port.close()


	def interrupt(self):
		self.interrupted = True
	
