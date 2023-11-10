import requests
import pandas as pd
import urllib
import collections
import json
import lxml.html as lh

from requests.exceptions import ConnectionError
from aisexplorer.Exceptions import (
    NotSupportedParameterTypeError,
    ProxiesNoLongerSupportedError,
    NotSupportedParameterError,
    CloudflareError,
    UserNotLoggedInError,
    NoResultsError,
)
from aisexplorer.Proxy import FreeProxy
from aisexplorer.Filters import Filters, FleetFilter
from tenacity import retry, stop_after_attempt, wait_fixed


def renew_proxy_and_retry(retry_state):
    """Renew the proxy and print a retry message.

    Args:
        retry_state (tenacity.RetryCallState): The current state of the retry logic.
    """
    obj = retry_state.args[0]
    obj.check_proxy()


def raise_no_results_error(retry_state):
    """Raise a NoResultsError after a certain number of attempts.

    Args:
        retry_state (tenacity.RetryCallState): The current state of the retry logic.

    Raises:
        NoResultsError: If no results are obtained after the specified attempts.
    """
    attempt_num = retry_state.attempt_number
    error_message = (
        f"After {attempt_num} attempts still no results are given. "
        f"If you think this is an error in the module raise an issue at "
        f"https://github.com/reyemb/AISExplorer "
    )
    raise NoResultsError(error_message)


class AIS:
    """A class to interact with the AISExplorer API with options for proxy and retry logic.

    Attributes:
        return_df (bool): If True, return a pandas DataFrame.
        return_total_count (bool): If True, return the total count of results.
        verbose (bool): If True, enable verbose output.
        columns (str or list): Column names to include in the results.
        columns_excluded (list): Column names to exclude from the results.
        print_query (bool): If True, print the query.
        logged_in (bool): If False, the user is not logged in.
        session (requests.Session): The session for HTTP requests.
        proxy (bool): If True, use a proxy.
        burned_proxies (list): List of proxies that have been used and are no longer viable.
    """

    retry_options = {
        "stop": stop_after_attempt(10),
        "wait": wait_fixed(15),
        "after": renew_proxy_and_retry,
        "retry_error_callback": raise_no_results_error,
    }

    def __init__(
        self,
        proxy=False,
        verbose=False,
        columns="all",
        columns_excluded=None,
        print_query=False,
        num_retries=10,
        seconds_wait=15,
        filter_config={},
        return_df=False,
        return_total_count=False,
        **proxy_config,
    ):
        """Initializes the AIS class with provided configurations."""
        self.update_retry_options(num_retries, seconds_wait)
        self.initialize_attributes(
            return_df,
            return_total_count,
            verbose,
            columns,
            columns_excluded,
            print_query,
        )
        self.configure_session(proxy, verbose, proxy_config)
        self.set_column_url()
        self.set_filters(filter_config=filter_config)

    def update_retry_options(self, num_retries, seconds_wait):
        """Update the retry options if they differ from the defaults."""
        if num_retries != 10:
            self.retry_options["stop"] = stop_after_attempt(num_retries)
        if seconds_wait != 15:
            self.retry_options["wait"] = wait_fixed(seconds_wait)

    def configure_session(self, proxy, verbose, proxy_config):
        """Configure the session with proxy settings and headers."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "Vessel-Image": "001b6192a3cc77daab750f70cab85f527b18",
            }
        )
        if proxy:
            raise ProxiesNoLongerSupportedError()
            self.setup_proxy(proxy_config, verbose=verbose)
        else:
            self.proxy = False

    def setup_proxy(self, proxy_config, verbose):
        """Set up the proxy using the provided configuration."""
        self.verbose_print("Searching for proxy...")
        self.freeproxy = (
            FreeProxy(**proxy_config, verbose=verbose)
            if proxy_config
            else FreeProxy(verbose=verbose)
        )
        self.session.proxies = self.freeproxy.get()
        self.verbose_print("Proxy found...")
        self.proxy = True
        self.burned_proxies = []

    def initialize_attributes(
        self,
        return_df,
        return_total_count,
        verbose,
        columns,
        columns_excluded,
        print_query,
    ):
        """Initialize instance attributes."""
        self.return_df = return_df
        self.return_total_count = return_total_count
        self.verbose = verbose
        self.columns = columns
        self.columns_excluded = columns_excluded
        self.print_query = print_query
        self.logged_in = False

    def login(self, email, password, use_proxy=False):
        """Attempt to log in to the AIS service.

        Args:
            email (str): The email address for login.
            password (str): The password for login.
            use_proxy (bool): Flag to determine if a proxy should be used for login.

        Raises:
            Exception: If the login fails.
        """
        if use_proxy and self.proxy:
            warnings.warn(
                "Login with proxy can be dangerous because of man-in-the-middle attacks. "
                "Although it is possible to use it, it is not recommended."
            )

        login_payload = {
            "_method": "POST",
            "email": email,
            "password": password,
        }
        login_headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en;q=0.6",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "vessel-image": "00a6f77ecb46da49c92b753fa98af9bed230",
            "x-requested-with": "XMLHttpRequest",
        }

        response = self.session.post(
            "https://www.marinetraffic.com/en/users/ajax_login",
            data=login_payload,
            headers=login_headers,
            proxies=self.session.proxies if use_proxy else None,
        )

        if response.status_code == 200:
            self.verbose_print("Login successful")
            self.logged_in = True
        else:
            self.verbose_print("Login failed. Check credentials and try again.")
            raise Exception(
                str(response.status_code)
                + "Login failed. Check credentials and try again."
                + response.text
            )  #

    def _ensure_logged_in(self):
        """Ensures that the user is logged in.

        Raises:
            UserNotLoggedInError: If the user is not logged in.
        """
        if not self.logged_in:
            raise UserNotLoggedInError("User must be logged in to perform this action.")

    def get_fleets(self):
        """Fetches fleets data from the AIS service.

        Raises:
            UserNotLoggedInError: If the user is not logged in.
            Exception: If the request fails with a non-200 status code.

        Returns:
            dict: The JSON response containing fleets data if the request is successful.
        """
        self._ensure_logged_in()
        response = self.session.get(
            "https://www.marinetraffic.com/en/search/fleetList",
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "vessel-image": "001b6192a3cc77daab750f70cab85f527b18",
                "x-requested-with": "XMLHttpRequest",
            },
        )
        if response.status_code == 200:
            self.verbose_print("Fetching fleets successful")
            return response.json()
        else:
            raise Exception(
                f"Something went wrong! {response.status_code}-{response.text}"
            )

    # @retry(**retry_options)
    def get_vessels_by_fleet_id(self, fleet_id: str):
        self._ensure_logged_in()
        fleets = self.get_fleets()
        for fleet in fleets:
            if fleet[0] == fleet_id:
                return self.get_data(fleets_filter=FleetFilter([[fleet[0], fleet[1]]]))
        raise Exception("Fleet not found")

    # @retry(**retry_options)
    def get_vessels_by_fleet_name(self, fleet_name: str):
        self._ensure_logged_in()
        fleets = self.get_fleets()
        for fleet in fleets:
            if fleet[1] == fleet_name:
                return self.get_data(fleets_filter=FleetFilter([[fleet[0], fleet[1]]]))
        raise Exception("Fleet not found")

    # @retry(**retry_options)
    def get_vessels_in_all_fleets(self):
        self._ensure_logged_in()
        if not self.logged_in:
            raise UserNotLoggedInError()
        fleets = self.get_fleets()
        return self.get_data(fleets_filter=FleetFilter(fleets))

    def set_filters(self, filter_config):
        """Set the filters for the query based on the provided configuration.

        Args:
            filter_config (dict): A dictionary containing filter configurations.
        """
        if not isinstance(filter_config, dict):
            raise ValueError("filter_config must be a dictionary.")
        self.filters = Filters(**filter_config)

    def set_column_url(self):
        """Set the column URL parameter for the data request."""
        possible_columns = [
            "time_of_latest_position",
            "flag",
            "shipname",
            "photo",
            "recognized_next_port",
            "reported_eta",
            "reported_destination",
            "current_port",
            "imo",
            "mmsi",
            "ship_type",
            "show_on_live_map",
            "area",
            "area_local",
            "lat_of_latest_position",
            "lon_of_latest_position",
            "fleet",
            "status",
            "eni",
            "speed",
            "course",
            "draught",
            "navigational_status",
            "year_of_build",
            "length",
            "width",
            "dwt",
            "current_port_unlocode",
            "current_port_country",
            "callsign",
        ]

        # Determine the columns to include based on exclusions and specified columns
        columns_to_include = self._determine_columns_to_include(possible_columns)

        # Join the columns into a string for the URL
        self.columns_url = ",".join(columns_to_include)

    def _determine_columns_to_include(self, possible_columns):
        """Determine which columns to include in the data request.

        Args:
            possible_columns (list): A list of all possible column names.

        Returns:
            list: A list of column names to include in the request.
        """
        if self.columns != "all":
            columns_selected = (
                self.columns if isinstance(self.columns, list) else [self.columns]
            )
        else:
            columns_selected = possible_columns

        if self.columns_excluded:
            if isinstance(self.columns_excluded, str):
                self.columns_excluded = [self.columns_excluded]

            if not all(isinstance(col, str) for col in self.columns_excluded):
                raise ValueError("All items in columns_excluded must be strings.")

            columns_selected = [
                col for col in columns_selected if col not in self.columns_excluded
            ]

        return columns_selected

    def verbose_print(self, message):
        """Print a message if verbose mode is enabled.

        Args:
            message (str): The message to be printed.
        """
        if self.verbose:
            print(message)

    def query_print(self, message):
        """Print the query message if query printing is enabled.

        Args:
            message (str): The query message to be printed.
        """
        if self.print_query:
            print(message)

    def check_proxy(self):
        """Check if the current proxy is working and renew it if not."""
        if self.proxy and not self.freeproxy.check_if_proxy_is_working(
            self.session.proxies
        ):
            self.verbose_print("Proxy has to be renewed.")
            self.renew_proxy()

    def renew_proxy(self):
        """Renew the proxy configuration."""
        self.verbose_print("Looking for a new proxy...")
        try:
            self.verbose_print("Old proxy: " + self.session.proxies["https"])
            self.session.proxies = self.freeproxy.get()
            self.verbose_print("New proxy: " + self.session.proxies["https"])
        except Exception as e:
            self.verbose_print(f"An error occurred while renewing proxy: {e}")

    @retry(**retry_options)
    def get_area_data(self, area):
        """
        Retrieves data for a specified geographic area from MarineTraffic.

        Args:
            area (str or iterable): The area(s) to retrieve data for. Can be a single string representing a valid area code
            or an iterable of area codes.

        Returns:
            dict: A dictionary containing the retrieved data.

        Raises:
            NotSupportedParameterError: If the provided area code(s) are not valid.

        Example:
            To retrieve data for the "Adriatic Sea," use:
            >>> data = get_area_data("ADRIA")

            To retrieve data for multiple areas, use an iterable:
            >>> data = get_area_data(["ADRIA", "BALTIC"])
        """
        _possible_areas = {
            "ADRIA": "Adriatic Sea",
            "AG": "Arabian Sea",
            "ALASKA": "Alaska",
            "ANT": "Antarctica",
            "BALTIC": "Baltic Sea",
            "BSEA": "Black Sea",
            "CARIBS": "Caribbean Sea",
            "CASPIAN": "Caspian Sea",
            "CCHINA": "Central China",
            "CISPAC": "CIS Pacific",
            "EAFR": "East Africa",
            "EAUS": "East Australia",
            "ECCA": "East Coast Central America",
            "ECCAN": "East Coast Canada",
            "ECI": "East Coast India",
            "ECSA": "East Coast South America",
            "EMED": "East Mediterranean",
            "GLAKES": "Great Lakes",
            "INDO": "Indonesia",
            "INLSAM": "Inland, South America",
            "INLCN": "Inland, China",
            "INLEU": "Inland, Europe",
            "INLRU": "Inland, Russia",
            "INLUS": "Inland, USA",
            "JAPAN": "Japan Coast",
            "NAUS": "North Australia",
            "NCCIS": "North Coast CIS",
            "NCHINA": "North China",
            "NCSA": "North Coast South America",
            "NOATL": "North Atlantic",
            "NORDIC": "Norwegian Coast",
            "NPAC": "North Pacific",
            "PHIL": "Philippines",
            "RSEA": "Red Sea",
            "SAFR": "South Africa",
            "SCHINA": "South China",
            "SEASIA": "South-East Asia",
            "SIND": "South Indian Ocean",
            "SPAC": "South Pacific",
            "UKC": "UK Coast & Atlantic",
            "USEC": "US East Coast",
            "USG": "Gulf of Mexico",
            "USWC": "US West Coast",
            "WAFR": "West Africa",
            "WAUS": "West Australia",
            "WCCA": "West Coast Central America",
            "WCCAN": "West Coast Canada",
            "WCI": "West Coast India",
            "WCSA": "West South America",
            "WMED": "West Mediterranean",
        }
        if isinstance(area, str):
            if area not in _possible_areas.keys():
                raise NotSupportedParameterError("area", _possible_areas.keys, area)
            areas_long = urllib.parse.quote_plus(area)
            area_short = area
        if isinstance(area, collections.abc.Iterable) and not isinstance(
            area, (str, bytes)
        ):
            for element in area:
                if element not in _possible_areas:
                    raise NotSupportedParameterError(
                        "area", _possible_areas.keys(), element
                    )
            areas_long = ",".join(
                [urllib.parse.quote_plus(_possible_areas[element]) for element in area]
            )
            area_short = ",".join(area)

        request_url = (
            f"https://www.marinetraffic.com/en/reports?asset_type=vessels&columns={self.columns_url}"
            f"&area_in|in|{areas_long}|area_in={area_short}{self.filters.to_query(ignore_filter='global_area')}"
        )
        referer_url = (
            f"https://www.marinetraffic.com/en/data/?asset_type=vessels&columns={self.columns_url}"
            f"&area_in|in|{areas_long}|area_in={area_short}{self.filters.to_query(ignore_filter='global_area')}"
        )
        self.query_print("referer_url: " + referer_url)
        self.query_print("request_url: " + request_url)
        return self.return_response(request_url, referer_url)

    @retry(**retry_options)
    def get_location(self, mmsi):
        """
        Retrieves location data for a vessel by its MMSI (Maritime Mobile Service Identity) from MarineTraffic.

        Args:
            mmsi (int or str): The MMSI of the vessel to retrieve location data for.

        Returns:
            dict: A dictionary containing the retrieved location data.

        Example:
            To retrieve location data for a vessel with MMSI 211281610, use:
            >>> location_data = get_location(211281610)
        """
        if isinstance(mmsi, int):
            mmsi = str(mmsi)
        request_url = (
            f"https://www.marinetraffic.com/en/reports?asset_type=vessels&columns={self.columns_url}"
            f"&mmsi|eq|mmsi={mmsi}{self.filters.to_query(ignore_filter='mmsi')}"
        )

        referer_url = (
            f"https://www.marinetraffic.com/en/data/?asset_type=vessels&columns={self.columns_url}"
            f"&mmsi|eq|mmsi={mmsi}{self.filters.to_query(ignore_filter='mmsi')}"
        )
        self.query_print("referer_url: " + referer_url)
        self.query_print("request_url: " + request_url)
        return self.return_response(request_url, referer_url)

    def get_data(self, use_Filters=False, fleets_filter=None):
        """
        Retrieves data from MarineTraffic based on specified filters and fleet options.

        Args:
            use_Filters (bool, optional): Whether to use the configured filters. Defaults to False.
            fleets_filter (FleetsFilter, optional): Fleet-specific filter to apply. Defaults to None.

        Returns:
            dict or str: If successful, returns the retrieved data as a dictionary. If there is an issue, returns an error message as a string.

        Example:
            To retrieve data using filters:
            >>> data = get_data(use_Filters=True)

            To retrieve data with fleet-specific filtering:
            >>> fleets_filter = FleetsFilter(...)
            >>> data = get_data(use_Filters=True, fleets_filter=fleets_filter)
        """
        if use_Filters:
            if fleets_filter is None:
                request_url = (
                    f"https://www.marinetraffic.com/en/reports?asset_type=vessels&columns={self.columns_url}"
                    f"{self.filters.to_query()}"
                )
                referer_url = (
                    f"https://www.marinetraffic.com/en/data/?asset_type=vessels&columns={self.columns_url}"
                    f"{self.filters.to_query()}"
                )
            else:
                request_url = (
                    f"https://www.marinetraffic.com/en/reports?asset_type=vessels&columns={self.columns_url},notes"
                    f"{self.filters.to_query()}{fleets_filter.to_request_query()}"
                )
                referer_url = (
                    f"https://www.marinetraffic.com/en/data/?asset_type=vessels&columns={self.columns_url},notes"
                    f"{self.filters.to_query()}{fleets_filter.to_referer_query()}"
                )
        else:
            if fleets_filter is None:
                request_url = f"https://www.marinetraffic.com/en/reports?asset_type=vessels&columns={self.columns_url}"
                referer_url = f"https://www.marinetraffic.com/en/data/?asset_type=vessels&columns={self.columns_url}"
            else:
                request_url = (
                    f"https://www.marinetraffic.com/en/reports?asset_type=vessels&columns={self.columns_url},notes"
                    f"{fleets_filter.to_request_query()}"
                )
                referer_url = (
                    f"https://www.marinetraffic.com/en/data/?asset_type=vessels&columns={self.columns_url},notes"
                    f"{fleets_filter.to_referer_query()}"
                )
        self.query_print("referer_url: " + referer_url)
        self.query_print("request_url: " + request_url)
        self.verbose_print("Getting data...")
        return self.return_response(request_url=request_url, referer_url=referer_url)

    @retry(**retry_options)
    def get_data_by_url(self, url):
        """
        Retrieves data from MarineTraffic using a provided URL.

        Args:
            url (str): The URL to retrieve data from.

        Returns:
            dict or str: If successful, returns the retrieved data as a dictionary. If there is an issue, returns an error message as a string.

        Example:
            To retrieve data from a specific URL:
            >>> url = "https://www.marinetraffic.com/en/reports?..."
            >>> data = get_data_by_url(url)
        """
        referer_url = url
        request_url = url.replace("data", "reports")
        return self.return_response(request_url, referer_url)

    def return_response(self, request_url, referer_url):
        """
        Sends an HTTP request to the specified URL and returns the response data.

        Args:
            request_url (str): The URL to send the HTTP request to.
            referer_url (str): The URL of the referring page.

        Returns:
            dict or str: If the request is successful, returns the response data as a dictionary. If there is an issue, returns an error message as a string.

        Example:
            To send an HTTP request and retrieve response data:
            >>> request_url = "https://www.marinetraffic.com/en/reports?..."
            >>> referer_url = "https://www.marinetraffic.com/en/data/?..."
            >>> data = return_response(request_url, referer_url)
        """
        try:
            self.check_proxy()
            response = self.session.get(
                request_url,
                headers={
                    # "Referer": referer_url,
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "vessel-image": "005bf958a6548a79c6d3a42eba493e339624",
                    "x-requested-with": "XMLHttpRequest",
                },
            )
        except ConnectionError as ce:
            self.verbose_print("Proxy has died. Looking for new proxy...")
            raise ce
        except Exception as e:
            self.verbose_print(f"An error occurred while sending the request: {e}")
            raise e
        self.check_response_cloudflare(response)

        self.verbose_print(f"Used proxy: {self.session.proxies}")
        if response.status_code == 200:
            if self.return_df:
                if self.return_total_count:
                    return (
                        pd.DataFrame(json.loads(response.text)["data"]),
                        json.loads(response.text)["totalCount"],
                    )
                else:
                    return pd.DataFrame(json.loads(response.text)["data"])
            else:
                if self.return_total_count:
                    return (
                        json.loads(response.text)["data"],
                        json.loads(response.text)["totalCount"],
                    )
                else:
                    return json.loads(response.text)["data"]
        else:
            return f"Response code: {str(response.status_code)} - headers: {self.session.headers} {response.text} - referer_url: {referer_url} - request_url: {request_url}"

    def check_response_cloudflare(self, response):
        """
        Checks if the response indicates Cloudflare protection and raises a CloudflareError if detected.

        Args:
            response (requests.Response): The HTTP response object to check.

        Raises:
            CloudflareError: If Cloudflare protection is detected in the response.

        Example:
            To check a response for Cloudflare protection:
            >>> response = self.session.get(request_url, headers={
            ...     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            ...     "vessel-image": "005bf958a6548a79c6d3a42eba493e339624",
            ...     "x-requested-with": "XMLHttpRequest"})
            >>> check_response_cloudflare(response)
        """
        doc = lh.fromstring(response.content)
        titles = doc.xpath("//title")
        if titles:
            title = titles[0].text_content()
            if "Cloudflare" in title:
                self.verbose_print(
                    f"Cloudflare has detected unusual behavior. Changing Proxy..."
                )
                raise CloudflareError()
