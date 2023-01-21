import unittest

from aisexplorer.Filters import Filters

class TestFilters(unittest.TestCase):
    def test_filter_1(self):
        self.assertEqual(Filters(mmsi=3812, dwt=[1, 2]).to_query(), "&mmsi|eq|mmsi=3812&dwt_between|range|dwt_between=1,2")

    def test_filter_2(self):
        self.assertEqual(Filters(latest_report= [360, 525600]).to_query(), "&time_of_latest_position_between|gte|time_of_latest_position_between=360,525600")

    def test_filter_3(self):
        self.assertEqual(Filters(lon=[20,30]).to_query(ignore_filter='vessel_name'), "&lon_of_latest_position_between|range|lon_of_latest_position_between=20,30")