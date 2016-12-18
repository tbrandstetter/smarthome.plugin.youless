#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2016 Thomas Brandstetter           thomas@brandstetter.co.at
#########################################################################
#  YouLess-Plugin for SmartHome.py.       https://github.com/smarthomeNG/
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
from lib.model.smartplugin import SmartPlugin
import json
import requests
import time

# Disable INFO messages from 'requests' to avoid unecessary
# log messages
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class YouLess(SmartPlugin):

    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = "1.2.1"

    def __init__(self, smarthome, host, port=80, cycle=300):
        self.logger = logging.getLogger('YouLess')
        self._sh = smarthome
        self._items = []
        self._values = {}
        self._host = host
        self._port = port
        self._timeout = 5
        self._cycle = int(cycle)
        self._context = "/a"
        self._payload = {'f' : 'j'}
        self._key2json = {
            'cnt' : 0,
            'pwr' : 0,
            'lvl' : 0,
            'dev' : 0,
            'det' : 0,
            'con' : "OK",
            'sts' : "0",
            'raw' : 0
        }

        if not self._host:
            self.logger.error("YouLess: Bad configuration, please add a YouLess IP")

    def run(self):
        self.alive = True
        self._sh.scheduler.add('YouLess', self._update_values, cycle=self._cycle)

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'youless' in item.conf:
            item_key = item.conf['youless']
            if item_key in self._key2json:
                self._items.append([item, item_key])
                return self.update_item
            else:
                self.logger.warn('invalid key {0} configured', item_key)
        return None

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'YouLess':
            pass

    def _update_values(self):
        data = self._get_data()

        for item_key in self._key2json:

            value = data[item_key]

            if item_key == "cnt":
              value = float(value.replace(',', '.'))

            self._values[item_key] = value

        for item_cfg in self._items:
            if item_cfg[1] in self._values:
                item_cfg[0](self._values[item_cfg[1]], 'YouLess')

    def _get_data(self):
        uri = "http://" + self._host + ":" + str(self._port) + self._context
        try:
            resp = requests.get(uri, params=self._payload)
        except:
            self.logger.error("YouLess: Could not open url: " + resp.status_code)

        data = resp.json()
        return data
