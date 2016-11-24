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
from signalk_client.datum import Datum

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
            #
            # TODO: this message should probably be handled somehow
            logging.warning(
                "unhandled hello message in delta stream: {!r}".format(data)
                )

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
                    self.__get_by_map_list(context_list),
                    indent=4, sort_keys=True
                    )
                ))
        else:
            logging.warning(
                "ignoring unrecognized delta message: {!r}".format(data)
                )

    def __get_by_map_list(self, map_list):
        """return a data object from a hierarchical list of keys"""
        value = reduce(lambda d, k: d[k], map_list, self.data)
        return value

    def __set_by_map_list(self, map_list, value):
        """set a data object at location based on a hierarchical list of keys"""
        self.__get_by_map_list(map_list[:-1])[map_list[-1]] = value

    def get_vessel_prop(self, path, vessel=None):
        """get data object from property path for vessel
        """
        return self.__get_by_map_list(
            ['vessels', vessel] + path.split('.')
            )

    def get_prop_meta(self, path):
        """get meta-data object from a property path
        """
        if self.meta.has_key(path):
            return self.meta[path]
        else:
            return {}

    def get_vessel_prop_datum(self, path, vessel=None):
        """returns a Datum object for the specified vessel's property path
        """
        value = None
        units = None
        desc = None

        got = self.get_vessel_prop(path, vessel)

        if isinstance(got, dict):
            value = got['value']
        else:
            value = got

        if self.meta.has_key(path):
            if self.meta[path].has_key('units'):
                units = self.meta[path]['units']
            if self.meta[path].has_key('description'):
                desc = self.meta[path]['description']
        return Datum(path, value, units, desc)

    def get_vessels(self):
        """returns a list of vessels signalk knows of
        """
        return self.data['vessels'].keys()

    def get_targets(self, vessel):
        """returns a list of available properties for vessel
        """
        out_targets = []
        for path in self.meta.keys():

            if path.find("*") > -1:

                logging.warning(
                    "Unhandled wildcard in target search for: {}".format(path)
                    )

            elif path.find("$") > -1:

                logging.warning(
                    "Unhandled reference in target search for: {}".format(path)
                    )

            else:

                try:
                    self.get_vessel_prop(path, vessel)
                except KeyError:
                    continue

                out_targets.append(path)

        return out_targets
