import unittest
import pandas as pd

from aisexplorer.AIS import AIS


class TestAis(unittest.TestCase):
    def test_return_type_df(self):
        self.assertIsInstance(
            AIS(verbose=False, return_df=True).get_area_data("WMED"), pd.DataFrame
        )

    def test_return_type_list(self):
        self.assertIsInstance(
            AIS(verbose=False, return_df=False).get_area_data("WMED"), list
        )

    def test_fetch_by_url(self):
        self.assertTrue(
            len(
                AIS(verbose=True, return_df=True).get_data_by_url(
                    "https://www.marinetraffic.com/en/data/?asset_type=vessels&columns=time_of_latest_position:desc,flag,shipname,photo,recognized_next_port,reported_eta,reported_destination,current_port,imo,ship_type,show_on_live_map,area,lat_of_latest_position,lon_of_latest_position,speed,length,width&area_in|in|West%20Mediterranean,East%20Mediterranean|area_in=WMED,EMED&time_of_latest_position_between|gte|time_of_latest_position_between=60,525600https://www.marinetraffic.com/en/data/?asset_type=vessels&columns=time_of_latest_position:desc,flag,shipname,photo,recognized_next_port,reported_eta,reported_destination,current_port,imo,ship_type,show_on_live_map,area,lat_of_latest_position,lon_of_latest_position,speed,length,width&area_in|in|West%20Mediterranean,East%20Mediterranean|area_in=WMED,EMED&time_of_latest_position_between|gte|time_of_latest_position_between=60,525600"
                )
            )
            > 100
        )

    def test_fetch_by_area(self):
        self.assertTrue(
            len(AIS(verbose=False, return_df=False).get_area_data("WMED")) > 100
        )
