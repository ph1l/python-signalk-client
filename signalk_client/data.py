# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
#   python-signalk-client is a python client library for SignalK
#   Copyright (C) 2016  Philip J Freeman <elektron@halo.nu>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""signalk data"""

import copy
import json
import logging
import pkg_resources
from signalk_client.vessel import Vessel

class Data(object):
    """signalk data object
    """

    def __init__(self, seed=None):

        self.meta = json.load(pkg_resources.resource_stream(
            'signalk_client', 'include/meta.json'
            ))

        if seed == None:
            # bare minimum valid schema
            self.data = {'version': "0.1.0", 'vessels': []}

        else:
            self.data = seed

            logging.debug(
                "loaded initial data:\n{}".format(
                    json.dumps(self.data, indent=2, sort_keys=True)
                    )
                )


    def process_delta(self, data):
        """Parse SignalK Delta message and update data store
        """

        if 'self' in data and 'version' in data and 'timestamp' in data:
            # hello message
            logging.debug(
                "hello message in delta stream: {!r}".format(data)
                )
            context_list = []
            update_properties = {}
            if 'self' in data:
                logging.info("setting self = {!r}".format(data['self']))
                self.__set_by_map_list(['self'], data['self'])
        elif 'updates' in data:
            # delta message
            if 'context' in data:
                context_list = data['context'].split(".")
            else:
                context_list = []
            for update in data['updates']:
                update_properties = {}
                if 'source' in update:
                    update_properties['source'] = update['source']
                if '$source' in update:
                    update_properties['$source'] = update['$source']
                if 'timestamp' in update:
                    update_properties['timestamp'] = update['timestamp']
                for value in update['values']:
                    item_in = copy.deepcopy(update_properties)
                    map_list = copy.deepcopy(context_list)
                    map_list += value['path'].split(".")
                    if isinstance(value['value'], dict):
                        for key in value['value'].keys():
                            item_in[key] = value['value'][key]
                    else:
                        item_in['value'] = value['value']
                    self.__set_by_map_list(map_list, item_in)
            logging.debug("updated context: {}\n{}".format(
                ".".join(context_list),
                json.dumps(
                    self.get_by_map_list(context_list),
                    indent=4, sort_keys=True
                    )
                ))
        else:
            logging.warning(
                "ignoring unrecognized delta message: {!r}".format(data)
                )

    def get_by_map_list(self, map_list):
        """return a data object from a hierarchical list of keys"""
        value = reduce(lambda d, k: d[k], map_list, self.data)
        return value

    def __set_by_map_list(self, map_list, value):
        """set a data object at location based on a hierarchical list of keys"""
        self.get_by_map_list(map_list[:-1])[map_list[-1]] = value

    def get_prop_meta(self, path):
        """get meta-data object from a property path
        """
        if self.meta.has_key(path):
            return self.meta[path]
        else:
            return {}

    def get_vessels(self):
        """returns a list of vessels (as Vessel objects) signalk knows of
        """
        vessels = []
        for vessel_key in self.data['vessels'].keys():
            vessels.append(Vessel(self, vessel_key))
        return vessels

    def get_self(self):
        """returns "self" vessel (as Vessel object)
        """
        vessels = []
        for vessel_key in self.data['vessels'].keys():
            vessels.append(Vessel(self, vessel_key))

        return Vessel(self, self.data['self'])
