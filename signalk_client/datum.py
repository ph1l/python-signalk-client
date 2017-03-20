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

"""dealing with individual data"""

import logging
import math
import re

FEET_PER_METER = 3.28084
METERS_PER_NAUTICAL_MILE = 1852
SECONDS_PER_HOUR = 60*60
KELVIN_CELSIUS_OFFSET = 273.15

DISPLAY_PATH_CONVERSIONS = [
    (re.compile(r"^environment\."), "env."),
    (re.compile(r"^navigation\."), "nav."),
    (re.compile(r"\.position\."), ".pos."),
    ]

def convert(value, from_unit, to_unit):
    """helper function to handle unit conversion"""

    if from_unit == 'm' and to_unit == 'ft':
        return value*FEET_PER_METER
    elif from_unit == 'm/s' and to_unit == 'kn':
        return value*SECONDS_PER_HOUR/METERS_PER_NAUTICAL_MILE
    elif from_unit == 'rad' and to_unit == 'deg':
        return 180 * value / math.pi
    elif from_unit == 'K' and to_unit == 'C':
        return value-KELVIN_CELSIUS_OFFSET
    elif from_unit == 'K' and to_unit == 'F':
        return ((value-KELVIN_CELSIUS_OFFSET)*(9.0/5.0))+32.0
    else:
        raise NotImplementedError(
            "Conversion from {} to {} is not supported".format(
                from_unit,
                to_unit
                )
            )

class Datum(object):
    """class for dealing with individual datums
    """
    def __init__(self, path, value=None, units=None, desc=None):
        self.path = path
        self.value = value
        self.desc = desc
        self.units = units

    def __str__(self):
        return "{}: {}".format(
            self.display_path(),
            self.display_value()
            )

    def display_path(self):
        """return the property path for display"""
        out_string = self.path
        for pattern, replacement in DISPLAY_PATH_CONVERSIONS:
            out_string = re.sub(pattern, replacement, out_string)
        return out_string

    def display_value(self, convert_units=None):
        """return the property value for display

        convert_units is a list of conversions to make

            convert_units = [('m', 'ft'), ('m/s', 'kn')]
        """
        value = self.value
        units = self.units

        if convert_units != None:
            for from_unit, to_unit in convert_units:
                if units == from_unit:
                    try:
                        value = convert(value, from_unit, to_unit)
                        units = to_unit
                    except TypeError:
                        logging.warn("Conversion ({} to {}) for {} ({}) failed".format(from_unit, to_unit, self.path, self.value))
        out_string = ""
        if value == None:
            out_string += "--"
        else:
            if self.path.endswith('.latitude'):
                direction = 'N' if value >= 0 else 'S'
                out_string += "{:.5f} {}".format(abs(value), direction)
            elif self.path.endswith('.longitude'):
                direction = 'E' if value >= 0 else 'W'
                out_string += "{:.5f} {}".format(abs(value), direction)
            elif isinstance(value, float):
                out_string += "{:.2f}".format(value)
            else:
                out_string += "{}".format(value)
            if units != None:
                out_string += " {}".format(units)
        return out_string
