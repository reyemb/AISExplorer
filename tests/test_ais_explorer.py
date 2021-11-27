from aisexplorer.AIS import AIS

#print(aisexplorer.AIS.get_area_data(["EMED", "WMED"]))

#print(aisexplorer.AIS.get_area_data("WMED"))

#print(aisexplorer.AIS.get_location(211281610))

print(AIS(verbose=True).get_area_data("WMED"))
