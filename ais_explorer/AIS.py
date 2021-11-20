import requests
import pandas as pd
import urllib
import collections
import json

from ais_explorer.Exceptions import NotSupportedParameterTypeError, NotSupportedParameterError


def get_area_data(area, columns="all", columns_excluded=None, return_df=False):
    possible_areas = {
        "ADRIA":	"Adriatic Sea",
        "AG":	"Arabian Sea",
        "ALASKA":	"Alaska",
        "ANT":	"Antarctica",
        "BALTIC":	"Baltic Sea",
        "BSEA":	"Black Sea",
        "CARIBS":	"Caribbean Sea",
        "CASPIAN":	"Caspian Sea",
        "CCHINA":	"Central China",
        "CISPAC":	"CIS Pacific",
        "EAFR":	"East Africa",
        "EAUS":	"East Australia",
        "ECCA":	"East Coast Central America",
        "ECCAN":	"East Coast Canada",
        "ECI":	"East Coast India",
        "ECSA":	"East Coast South America",
        "EMED":	"East Mediterranean",
        "GLAKES":	"Great Lakes",
        "INDO":	"Indonesia",
        "INLSAM":	"Inland, South America",
        "INLCN":	"Inland, China",
        "INLEU":	"Inland, Europe",
        "INLRU":	"Inland, Russia",
        "INLUS":	"Inland, USA",
        "JAPAN":	"Japan Coast",
        "NAUS":	"North Australia",
        "NCCIS":	"North Coast CIS",
        "NCHINA":	"North China",
        "NCSA":	"North Coast South America",
        "NOATL":	"North Atlantic",
        "NORDIC":	"Norwegian Coast",
        "NPAC":	"North Pacific",
        "PHIL":	"Philippines",
        "RSEA":	"Red Sea",
        "SAFR":	"South Africa",
        "SCHINA":	"South China",
        "SEASIA":	"South-East Asia",
        "SIND":	"South Indian Ocean",
        "SPAC":	"South Pacific",
        "UKC":	"UK Coast & Atlantic",
        "USEC":	"US East Coast",
        "USG":	"Gulf of Mexico",
        "USWC":	"US West Coast",
        "WAFR":	"West Africa",
        "WAUS":	"West Australia",
        "WCCA":	"West Coast Central America",
        "WCCAN":	"West Coast Canada",
        "WCI":	"West Coast India",
        "WCSA":	"West South America",
        "WMED":	"West Mediterranean"
    }
    possible_columns = ["time_of_latest_position", "flag", "shipname", "photo", "recognized_next_port", "reported_eta", "reported_destination", "current_port", "imo", "mmsi", "ship_type", "show_on_live_map", "area", "area_local", "lat_of_latest_position", "lon_of_latest_position", "fleet", "status", "eni", "speed", "course", "draught", "navigational_status", "year_of_build", "length", "width", "dwt", "current_port_unlocode", "current_port_country", "callsign"]
    if columns != "all":
        columns_selected = columns
    else:
        columns_selected = possible_columns

    if columns_excluded is not None:
        if isinstance(columns_excluded, str) or isinstance(columns_excluded, collections.abc.Iterable):
            if isinstance(columns_excluded, str):
                try:
                    columns_selected.remove(columns_excluded)
                except ValueError:
                    raise NotSupportedParameterError("exclude",possible_columns, columns_excluded)
            if isinstance(columns_excluded, collections.abc.Iterable) and not isinstance(columns_excluded, (str, bytes)):
                for element in columns_excluded:
                    try:
                        possible_columns.remove(element)
                    except ValueError:
                        raise NotSupportedParameterError("exclude", possible_columns, element)
        else:
            raise NotSupportedParameterTypeError("exclude", "collections.abc.Iterable or str", type(columns_excluded))

    if isinstance(columns_selected, str):
        columns_url = columns_selected
    else:
        columns_url = ",".join(columns_selected)

    if isinstance(area, str):
        if area not in possible_areas.keys():
            raise NotSupportedParameterError("area", possible_areas.keys, area)
        areas_long = urllib.parse.quote_plus(area)
        area_short = area
    if isinstance(area, collections.abc.Iterable) and not isinstance(area, (str, bytes)):
        for element in area:
            if element not in possible_areas:
                raise NotSupportedParameterError("area", possible_areas.keys(), element)
        areas_long = ",".join([urllib.parse.quote_plus(possible_areas[element]) for element in area])
        area_short = ",".join(area)

    request_url = f"https://www.marinetraffic.com/en/reports?asset_type=vessels&columns={columns_url}&area_in={area_short}&time_of_latest_position_between=60,NaN"
    referer_url = f"https://www.marinetraffic.com/en/data/?asset_type=vessels&columns={columns_url}&area_in|in|{areas_long}|area_in={area_short}&time_of_latest_position_between|gte|time_of_latest_position_between=60,525600"

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
        'Vessel-Image': '005bf958a6548a79c6d3a42eba493e339624',
        'Referer': referer_url
    }

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        if return_df:
            return pd.DataFrame(json.loads(response.text)["data"])
        else:
            return json.loads(response.text)["data"]
    else:
        return response.text


def get_location(mmsi, columns="all", columns_excluded=None, return_df=False):
    if isinstance(mmsi, int):
        mmsi = str(mmsi)
    possible_columns = ["time_of_latest_position", "flag", "shipname", "photo", "recognized_next_port", "reported_eta", "reported_destination", "current_port", "imo", "mmsi", "ship_type", "show_on_live_map", "area", "area_local", "lat_of_latest_position", "lon_of_latest_position", "fleet", "status", "eni", "speed", "course", "draught", "navigational_status", "year_of_build", "length", "width", "dwt", "current_port_unlocode", "current_port_country", "callsign"]
    if columns != "all":
        columns_selected = columns
    else:
        columns_selected = possible_columns

    if columns_excluded is not None:
        if isinstance(columns_excluded, str) or isinstance(columns_excluded, collections.abc.Iterable):
            if isinstance(columns_excluded, str):
                try:
                    columns_selected.remove(columns_excluded)
                except ValueError:
                    raise NotSupportedParameterError("exclude",possible_columns, columns_excluded)
            if isinstance(columns_excluded, collections.abc.Iterable) and not isinstance(columns_excluded, (str, bytes)):
                for element in columns_excluded:
                    try:
                        possible_columns.remove(element)
                    except ValueError:
                        raise NotSupportedParameterError("exclude", possible_columns, element)
        else:
            raise NotSupportedParameterTypeError("exclude", "collections.abc.Iterable or str", type(columns_excluded))

    if isinstance(columns_selected, str):
        columns_url = columns_selected
    else:
        columns_url = ",".join(columns_selected)

    request_url = f"https://www.marinetraffic.com/en/reports?asset_type=vessels&columns={columns_url}&mmsi|eq|mmsi={mmsi}"
    referer_url = f"https://www.marinetraffic.com/en/data/?asset_type=vessels&columns={columns_url}&mmsi|eq|mmsi={mmsi}"

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
        'Vessel-Image': '005bf958a6548a79c6d3a42eba493e339624',
        'Referer': referer_url
    }

    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        if return_df:
            return pd.DataFrame(json.loads(response.text)["data"])
        else:
            return json.loads(response.text)["data"]
    else:
        return response.text

