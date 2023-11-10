import random
import sys
import time
import lxml.html as lh
import requests
import pandas as pd
import collections
import warnings
from typing import Union, Iterable, Optional, Dict


def check_valid_ip(string: str) -> bool:
    """Check if a given string is a valid IP address."""
    parts = string.strip().split(".")
    return len(parts) == 4 and all(
        part.isnumeric() and 0 <= int(part) <= 255 for part in parts
    )


def convert_str_to_bool(string: str) -> bool:
    """Convert a string to a boolean value based on predefined mappings."""
    return {"yes": True, "": False, "no": False}.get(string, False)


def clean_dataframe_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Clean a specific column in a DataFrame by converting strings to boolean values."""
    if column_name in df.columns:
        df[column_name] = df[column_name].apply(convert_str_to_bool)
    return df


class FreeProxy:
    """A class to manage fetching and filtering free proxy lists."""

    def __init__(
        self,
        timeout: float = 0.5,
        rand: bool = True,
        https: bool = True,
        refresh_after: int = 900,
        verbose: bool = False,
        **filters,
    ):
        self.timeout = timeout
        self.random = rand
        self.https = https
        self.refresh_after = refresh_after
        self.verbose = verbose
        self.filters = filters
        self.proxies = None
        self.fetched_at = None
        self.filtered_df = None

    def verbose_print(self, message: str):
        """Print a message if verbose mode is enabled."""
        if self.verbose:
            print(message)

    def series_to_proxy(self, series: pd.Series) -> Dict[str, str]:
        """Convert a series from a DataFrame to a proxy dictionary."""
        protocol = "https" if self.https else "http"
        return {protocol: f"{series.name}:{series['port']}"}

    def fetch_proxy_list(self):
        """Fetch the list of proxies from the web and clean the DataFrame."""
        try:
            page = requests.get("https://www.sslproxies.org")
            doc = lh.fromstring(page.content)
            list_proxies = []
            tr_elements = doc.xpath('//*[@id="list"]//tr')
            for tr_element in tr_elements:
                if (
                    check_valid_ip(tr_element[0].text_content())
                    and tr_element[0].text_content() is not None
                ):
                    dict_tmp = {}
                    for counter, attribute in enumerate(
                        [
                            "ip_address",
                            "port",
                            "country_code",
                            "country",
                            "anonymity",
                            "google",
                            "https",
                            "last_checked",
                        ]
                    ):
                        dict_tmp[attribute] = tr_element[counter].text_content()
                    list_proxies.append(dict_tmp)
            self.proxies = pd.DataFrame(list_proxies).set_index("ip_address")
            self.proxies = clean_dataframe_column(self.proxies, "google")
            self.proxies = clean_dataframe_column(self.proxies, "https")
            self.fetched_at = time.time()
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

    def get_filtered_proxies(self) -> pd.DataFrame:
        """Filter the DataFrame of proxies based on the given filters."""
        if self.proxies is None:
            self.fetch_proxy_list()
        elif time.time() - self.fetched_at >= self.refresh_after:
            self.fetch_proxy_list()

        conditions = []
        for key, value in self.filters.items():
            if isinstance(value, bool):
                conditions.append(f"(self.proxies['{key}'] == {value})")
            elif isinstance(value, str):
                conditions.append(f"(self.proxies['{key}'] == '{value}')")
            elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                conditions.append(f"(self.proxies['{key}'].isin({list(value)}))")

        filter_str = " & ".join(conditions)
        return self.proxies.query(filter_str) if filter_str else self.proxies

    def find_working_proxy(self) -> Optional[Dict[str, str]]:
        """Find a working proxy from the filtered DataFrame."""
        self.filtered_df = self.get_filtered_proxies()
        if self.filtered_df.empty:
            return None

        proxy_list = (
            self.filtered_df.sample(frac=1) if self.random else self.filtered_df
        )
        for _, proxy_series in proxy_list.iterrows():
            proxy = self.series_to_proxy(proxy_series)
            if self.check_if_proxy_is_working(proxy):
                return proxy
        return None

    def check_if_proxy_is_working(self, proxy: Dict[str, str]) -> bool:
        """Check if a given proxy is working."""
        protocol = "https" if self.https else "http"
        try:
            r = requests.get(
                f"{protocol}://github.com/reyemb/AISExplorer/",
                proxies=proxy,
                timeout=self.timeout,
            )
            self.verbose_print(f"Proxy {proxy} returned status code {r.status_code}")
            return r.status_code == 200
        except Exception as e:
            self.verbose_print(f"Proxy {proxy} failed with exception {e}")
            return False

    def get(self) -> Optional[Dict[str, str]]:
        """Get a working proxy."""
        working_proxy = self.find_working_proxy()
        if working_proxy:
            return working_proxy

        warnings.warn("No working proxies found. Expanding search.")
        self.filters.pop("prefered_country", None)
        self.filters.pop("prefered_country_code", None)
        return self.find_working_proxy()
