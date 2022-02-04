from aisexplorer.AIS import AIS
from aisexplorer.Filters import Filters
from aisexplorer.Utils.Utility import set_types_df

# Return Vessels in WMED-Area
# print(AIS(verbose=True, return_df=True).get_area_data("WMED"))

# Return Vessel in WMED-Area using Proxy
# print(AIS(verbose=True, proxy=True).get_area_data("WMED"))

# Get Data via URL
# print(AIS(verbose=True, proxy=True, num_retries=10, return_df=True).get_data_by_url("https://www.marinetraffic.com/en/data/?asset_type=vessels&columns=time_of_latest_position:desc,flag,shipname,photo,recognized_next_port,reported_eta,reported_destination,current_port,imo,ship_type,show_on_live_map,area,lat_of_latest_position,lon_of_latest_position,speed,length,width&area_in|in|West%20Mediterranean,East%20Mediterranean|area_in=WMED,EMED&time_of_latest_position_between|gte|time_of_latest_position_between=60,525600https://www.marinetraffic.com/en/data/?asset_type=vessels&columns=time_of_latest_position:desc,flag,shipname,photo,recognized_next_port,reported_eta,reported_destination,current_port,imo,ship_type,show_on_live_map,area,lat_of_latest_position,lon_of_latest_position,speed,length,width&area_in|in|West%20Mediterranean,East%20Mediterranean|area_in=WMED,EMED&time_of_latest_position_between|gte|time_of_latest_position_between=60,525600"))

# Check filters
#print(Filters(mmsi=3812, dwt=[1, 2]).to_query())

# Check filters
print(Filters(latest_report= [360, 525600]).to_query())

print(Filters(lon=[20,30]).to_query(ignore_filter='vessel_name'))

ais = AIS(verbose=True, return_df=True, return_total_count=True, print_query=True)

df, total_count = ais.get_area_data("WMED")

print(df.iloc[0])

ais.set_filters({'vessel_name': 'B'})

df, total_count = ais.get_area_data("WMED")

print(df.iloc[1])

print(df)
print(total_count)

print("|" == "|")
