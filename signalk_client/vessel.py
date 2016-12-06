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

import logging

from signalk_client.datum import Datum

"""vessel objects"""

class Vessel(object):
    """Vessel Object

    Keyword arguments:
    data -- SignalK Data object
    vessel_key -- dictionary key for vessel
    """
    def __init__(self, data, vessel_key):
        self.key = vessel_key
        self.data = data
        self._load_vessel_data()

    def __str__(self):
        if self.name:
            return self.name
        elif self.mmsi:
            return "MMSI: {}".format(self.mmsi)
        elif self.uuid:
            return "UUID: {}".format(self.uuid)
        elif self.url:
            return "URL: {}".format(self.url)

        return "KEY: {}".format(self.key)

    def _load_vessel_data(self):
        """load vessel data from signalk"""
        # set some defaults
        self.uuid = None
        self.mmsi = None
        self.url = None
        self.name = None

        # lookup stuff
        try:
            self.uuid = self.get_datum('uuid').display_value()
        except (KeyError, TypeError):
            pass

        try:
            self.mmsi = self.get_datum('mmsi').display_value()
        except (KeyError, TypeError):
            pass

        try:
            self.url = self.get_datum('url').display_value()
        except (KeyError, TypeError):
            pass

        #SignalK Requires one of the above settings
        assert(self.uuid or self.mmsi or self.url)

        try:
            self.name = self.get_datum('name').display_value()
        except (KeyError, TypeError):
            pass

    def get_targets(self):
        """returns a list of available properties for vessel
        """
        out_targets = []
        for path in self.data.meta.keys():

            if path.find("*") > -1:

                # TODO: Support wildcard paths in target scan
                logging.warning(
                    "Unhandled wildcard in target search for: {}".format(path)
                    )

            elif path.find("$") > -1:

                # TODO: Support reference paths in target scan ???
                logging.warning(
                    "Unhandled reference in target search for: {}".format(path)
                    )

            else:

                try:
                    self.get_datum(path)
                except KeyError:
                    continue

                out_targets.append(path)

        return sorted(out_targets)

    def get_prop(self, path):
        """get raw data for vessel's property

        Keyword arguments:
            path -- a signalk property path

        this returns a raw object (or whatever data exists) for the provided
        signalk property path.
        """
        return self.data.get_by_map_list(
            ['vessels', self.key] + path.split('.')
            )

    def get_datum(self, path):
        """get a Datum object for vessel's property
        """
        value = None
        units = None
        desc = None

        got = self.get_prop(path)

        if isinstance(got, dict):
            value = got['value']
        else:
            value = got

        if self.data.meta.has_key(path):
            if self.data.meta[path].has_key('units'):
                units = self.data.meta[path]['units']
            if self.data.meta[path].has_key('description'):
                desc = self.data.meta[path]['description']
        return Datum(path, value, units, desc)
