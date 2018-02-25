# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

class HelloWorldPlugin(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin):
	def on_after_startup(self):
    		self._logger.info("Hello World!")

	def get_settings_defaults(self):
	    return dict(
		comport="COM3",
		url="https://en.wikipedia.org/wiki/Hello_world"
		)

	def get_config_vars(self):
		return dict(
			comport=self._settings.get(["comport"])
		)

	def get_template_configs(self):
	    return [
        	dict(type="navbar", custom_bindings=False),
	        dict(type="settings", custom_bindings=False)
	    ]

__plugin_name__ = "Arduino Safety"
__plugin_implementation__ = HelloWorldPlugin()
