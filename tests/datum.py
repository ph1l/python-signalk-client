# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import unittest
import signalk_client.datum as datum

class TestDatumConvert(unittest.TestCase):

    def test_datum_convert_meters_to_feet(self):
        self.assertEqual(datum.convert(1.0, 'm', 'ft'), 3.28084)

    def test_datum_convert_meters_per_second_to_knots(self):
        self.assertAlmostEqual(datum.convert(1.0, 'm/s', 'kn'), 1.94384, places=5)

    def test_datum_convert_radians_to_degrees(self):
        self.assertAlmostEqual(datum.convert(1.0, 'rad', 'deg'), 57.2958, places=4)

    def test_datum_convert_kelvin_to_celsius(self):
        self.assertAlmostEqual(datum.convert(1.0, 'K', 'C'), -272.15, places=2)

    def test_datum_convert_kelvin_to_fahrenheit(self):
        self.assertAlmostEqual(datum.convert(1.0, 'K', 'F'), -457.87, places=2)

    def test_datum_convert_raises_notimplementederror(self):
        with self.assertRaises(NotImplementedError):
            datum.convert(1.0, 'blah', 'bleh')
