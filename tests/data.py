# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import unittest
import signalk_client.data as data

class TestDataInitialization(unittest.TestCase):

    def setUp(self):
        self.data = data.Data()

    def test_data_initial_structure(self):
        self.assertEqual(self.data.data.has_key('version'), True);
        self.assertEqual(type(self.data.data['version']), str);
        self.assertEqual(self.data.data.has_key('vessels'), True);
        self.assertEqual(type(self.data.data['vessels']), list);
