import requests
import pandas as pd
import urllib
import collections
import json
import lxml.html as lh

from requests.exceptions import ConnectionError
from aisexplorer.Exceptions import NotSupportedParameterTypeError, NotSupportedParameterError, NoResultsError, \
    CloudflareError
from aisexplorer.Proxy import FreeProxy
from aisexplorer.Filters import Filters
from tenacity import retry, stop_after_attempt, wait_fixed


def before_retry(retry_state):
    object = retry_state.args[0]
    if object.proxy:
        object.verbose_print(retry_state.outcome.result)
        object.verbose_print("Renewing Proxy and trying again in 15 seconds")
        object.renew_proxy()
    else:
        object.verbose_print("Retrying again in 15 seconds")


def error_callback(retry_state):
    raise NoResultsError(f"After {str(retry_state.attempt_number)} Attempts still no results are given. "
                         f"If you think this is an Error in the module raise an Issue at "
                         f"https://github.com/reyemb/AISExplorer ")


class AIS:
    retry_options = {
        "stop": stop_after_attempt(10),
        "wait": wait_fixed(15),
        "after": before_retry,
        "retry_error_callback": error_callback
    }
    def __init__(self, proxy=False, verbose=False, columns="all", columns_excluded=None, print_query = False,
                 num_retries=10, seconds_wait=15, filter_config={}, return_df=False, return_total_count=False,
                 **proxy_config):
        # Setting Retry Options
        if num_retries != 10:
            AIS.retry_options['stop'] = stop_after_attempt(num_retries)
        if seconds_wait != 15:
            AIS.retry_options['wait'] = wait_fixed(seconds_wait)

        self.return_df = return_df
        self.return_total_count = return_total_count
        self.verbose = verbose
        self.columns = columns
        self.columns_excluded = columns_excluded
        self.print_query = print_query
        self.session = requests.Session()
        self.set_filters(filter_config)
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
            'Vessel-Image': '005bf958a6548a79c6d3a42eba493e339624',
        })
        self.set_column_url()
        if proxy:
            if proxy_config.get('proxy_config') is not None:
                self.freeproxy = FreeProxy(**proxy_config.get('proxy_config'))
            else:
                self.freeproxy = FreeProxy()
            self.verbose_print("Searching for proxy...")
            self.session.proxies = self.freeproxy.get()
            self.verbose_print("Proxy found...")
            self.proxy = proxy
            self.burned_proxies = []
        else:
            self.proxy = False

    def set_filters(self, filter_config):
        self.filters = Filters(**filter_config)

    def set_column_url(self):
        possible_columns = ["time_of_latest_position", "flag", "shipname", "photo", "recognized_next_port",
                            "reported_eta", "reported_destination", "current_port", "imo", "mmsi", "ship_type",
                            "show_on_live_map", "area", "area_local", "lat_of_latest_position",
                            "lon_of_latest_position", "fleet", "status", "eni", "speed", "course", "draught",
                            "navigational_status", "year_of_build", "length", "width", "dwt", "current_port_unlocode",
                            "current_port_country", "callsign"]
        if self.columns != "all":
            columns_selected = self.columns
        else:
            columns_selected = possible_columns

        if self.columns_excluded is not None:
            if isinstance(self.columns_excluded, str) or isinstance(self.columns_excluded, collections.abc.Iterable):
                if isinstance(self.columns_excluded, str):
                    try:
                        columns_selected.remove(self.columns_excluded)
                    except ValueError:
                        raise NotSupportedParameterError("exclude", possible_columns, self.columns_excluded)
                if isinstance(self.columns_excluded, collections.abc.Iterable) and \
                        not isinstance(self.columns_excluded, (str, bytes)):
                    for element in self.columns_excluded:
                        try:
                            possible_columns.remove(element)
                        except ValueError:
                            raise NotSupportedParameterError("exclude", possible_columns, element)
            else:
                raise NotSupportedParameterTypeError("exclude", "collections.abc.Iterable or str",
                                                     type(self.columns_excluded))

        if isinstance(columns_selected, str):
            columns_url = columns_selected
        else:
            columns_url = ",".join(columns_selected)
        self.columns_url = columns_url

    def verbose_print(self, message):
        if self.verbose:
            print(message)

    def query_print(self, message):
        if self.print_query:
            print(message)

    def check_proxy(self):
        if self.proxy:
            if not self.freeproxy.check_if_proxy_is_working(self.session.proxies):
                self.verbose_print("Proxy has to be renewed")
                self.verbose_print("Looking for new proxy...")
                self.session.proxies = self.freeproxy.get()
                self.verbose_print("Proxy found...")

    def renew_proxy(self):
        self.verbose_print("Looking for new proxy...")
        self.session.proxies = self.freeproxy.get()
        self.verbose_print("Proxy found...")

    @retry(**retry_options)
    def get_area_data(self, area):
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

        request_url = f"https://www.marinetraffic.com/en/reports?asset_type=vessels&columns={self.columns_url}" \
                      f"&area_in|in|{areas_long}|area_in={area_short}{self.filters.to_query(ignore_filter='global_area')}"
        referer_url = f"https://www.marinetraffic.com/en/data/?asset_type=vessels&columns={self.columns_url}" \
                      f"&area_in|in|{areas_long}|area_in={area_short}{self.filters.to_query(ignore_filter='global_area')}"
        self.query_print("referer_url: " + referer_url)
        self.query_print("request_url: " + request_url)
        return self.return_response(request_url, referer_url)

    @retry(**retry_options)
    def get_location(self, mmsi):
        if isinstance(mmsi, int):
            mmsi = str(mmsi)
        request_url = f"https://www.marinetraffic.com/en/reports?asset_type=vessels&columns={self.columns_url}" \
                      f"&mmsi|eq|mmsi={mmsi}{self.filters.to_query(ignore_filter='mmsi')}"
        referer_url = f"https://www.marinetraffic.com/en/data/?asset_type=vessels&columns={self.columns_url}" \
                      f"&mmsi|eq|mmsi={mmsi}{self.filters.to_query(ignore_filter='mmsi')}"
        self.query_print("referer_url: " + referer_url)
        self.query_print("request_url: " + request_url)
        return self.return_response(request_url, referer_url)

    @retry(**retry_options)
    def get_data_by_url(self, url):
        referer_url = url
        request_url = url.replace("data", "reports")
        return self.return_response(request_url, referer_url)

    def return_response(self, request_url, referer_url):
        self.session.headers['Referer'] = referer_url
        try:
            response = self.session.get(request_url)
        except ConnectionError as ce:
            self.verbose_print('Proxy has died. Looking for new proxy...')
            raise ce
        self.check_response_cloudflare(response)
        self.verbose_print(f"Used proxy: {self.session.proxies}")
        if response.status_code == 200:
            if self.return_df:
                if self.return_total_count:
                    return pd.DataFrame(json.loads(response.text)["data"]), json.loads(response.text)["totalCount"]
                else:
                    return pd.DataFrame(json.loads(response.text)["data"])
            else:
                if self.return_total_count:
                    return json.loads(response.text)["data"], json.loads(response.text)["totalCount"]
                else:
                    return json.loads(response.text)["data"]
        else:
            return response.text

    def check_response_cloudflare(self, response):
        doc = lh.fromstring(response.content)
        titles = doc.xpath('//title')
        if titles:
            title = titles[0].text_content()
            if "Cloudflare" in title:
                self.verbose_print(f"Cloudflare has detected unusual behavior. Changing Proxy...")
                raise CloudflareError()