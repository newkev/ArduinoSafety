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
		comport="COM3",
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

	#	comport = "COM3",#
	# baudrate = 9600,

	def __init__(self, callbackClass, config):
		Thread.__init__(self)
		self.cbClass = callbackClass
		self.portname = config["comport"]
		self.baudrate = config["baudrate"]

		try:
			self.port = serial.Serial(self.portname, baudrate=self.baudrate, timeout=3.0)
		except:
			self.interrupt()
			callbackClass.getLogger().error("Octoremote, could not open comport:" + self.portname)
		callbackClass.getLogger().info("Octoremote Comthread started")
		self.daemon = False
		self.start()

	def run(self):
		self.cbClass.getLogger().info("Thread started")

		while not self.interrupted:
			try:
				readbyte = self.port.read(1)
				if self.msgParsingState == 0:
					if readbyte == '\x80':
						self.bytesRead.append(ord(readbyte))
						self.msgParsingState += 1
						self.countBytesRead += 1

				elif self.msgParsingState == 1:
					self.telegramLength = ord(readbyte)
					self.bytesRead.append(ord(readbyte))
					self.msgParsingState += 1
					self.countBytesRead += 1

				elif self.msgParsingState == 2:
					self.command = ord(readbyte)
					self.bytesRead.append(ord(readbyte))
					self.msgParsingState += 1
					self.countBytesRead += 1
					if self.telegramLength == 7:
						self.msgParsingState += 1

				elif self.msgParsingState == 3:
					self.bytesRead.append(ord(readbyte))
					self.payload.append(ord(readbyte))
					self.countBytesRead += 1
					if self.countBytesRead == self.telegramLength - 4:
						self.msgParsingState += 1
				elif self.msgParsingState == 4:
					self.crc32 = ord(readbyte)
					self.countBytesRead += 1
					self.msgParsingState += 1

				elif self.msgParsingState == 5:
					self.crc32 |= ord(readbyte) << 8
					self.countBytesRead += 1
					self.msgParsingState += 1

				elif self.msgParsingState == 6:
					self.crc32 |= ord(readbyte) << 16
					self.countBytesRead += 1
					self.msgParsingState += 1

				elif self.msgParsingState == 7:
					self.crc32 |= ord(readbyte) << 24
					self.countBytesRead += 1
					self.msgParsingState += 1
					crc32 = binascii.crc32(bytearray(self.bytesRead)) % (1 << 32)
					if crc32 == self.crc32:
						self.performActions(self.command, self.payload)
					else:
						self.sendNack()

					self.msgParsingState = 0
					self.crc32 = 0
					self.countBytesRead = 0
					self.bytesRead = []
					self.payload = []
					self.telegramLength = 0
					self.command = 0
			except:
				pass
		self.port.close()


	def interrupt(self):
		self.interrupted = True
	
