# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import unittest
import signalk_client.data as data
import signalk_client.vessel as vessel

class TestVesselInitialization(unittest.TestCase):

    def setUp(self):
        self.data = data.Data()

    def test_vessel_unknown(self):
        with self.assertRaises(AssertionError):
            self.vessel = vessel.Vessel(self.data, "unknown")
