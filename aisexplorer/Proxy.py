import random
import sys
import time
import lxml.html as lh
import requests
import pandas as pd
import collections
import warnings

from typing import Union


def check_valid_ip(string: str) -> bool:
    valid = False
    if "." in string:
        elements_array = string.strip().split(".")
        if len(elements_array) == 4:
            for i in elements_array:
                if i.isnumeric() and int(i) >= 0 and int(i) <= 255:
                    valid = True
                else:
                    valid = False
                    break
    return valid


dict_str = {
    'yes': True,
    '': False,
    'no': False,
}


def convert_str_to_bool(string: str) -> bool:
    return dict_str.get(string)


list_columns_to_clean = ['google', 'https']


def clean_dataframe(df: pd.DataFrame):
    for column in list_columns_to_clean:
        if column in df.columns:
            df[column] = df[column].apply(lambda x: convert_str_to_bool(x))
    return df


class FreeProxy:
    def __init__(self, country: Union[str, collections.abc.Iterable] = None,
                 country_code: Union[str, collections.abc.Iterable] = None,
                 timeout: float = 0.5, anonym: Union[str, bool] = None, rand: bool = True,
                 https: Union[bool, str] = True,
                 prefered_country: Union[str, collections.abc.Iterable] = None,
                 prefered_country_code: Union[str, collections.abc.Iterable] = None,
                 refresh_after: int = 900):
        self.country = country
        self.country_code = country_code
        self.prefered_country = prefered_country
        self.prefered_country_code = prefered_country_code
        self.timeout = timeout
        self.anonym = anonym
        self.https = https
        self.random = rand
        self.proxies = None
        self.fetched_at = None
        self.refresh_after = refresh_after
        self.filtered_df = None

    def series_to_proxy(self, series) -> dict:
        http_str = 'https' if self.https else 'http'
        proxy_set = {
            http_str: f"{series.name}:{series['port']}"
        }
        return proxy_set, series.name

    def get_proxy_list(self):
        try:
            page = requests.get('https://www.sslproxies.org')
            doc = lh.fromstring(page.content)
            tr_elements = doc.xpath('//*[@id="list"]//tr')
            list_proxies = []
            for tr_element in tr_elements:
                if check_valid_ip(tr_element[0].text_content()) and tr_element[0].text_content() is not None:
                    dict_tmp = {}
                    for counter, attribute in enumerate(
                            ['ip_address', 'port', ' country_code', 'country', 'anonymity', 'google', 'https',
                             'last_checked']):
                        dict_tmp[attribute] = tr_element[counter].text_content()
                    list_proxies.append(dict_tmp)
            self.proxies = pd.DataFrame(list_proxies)
            self.proxies = self.proxies.set_index('ip_address')
            self.proxies = clean_dataframe(self.proxies)
            self.fetched_at = time.time()
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

    @staticmethod
    def get_filter_str(country: Union[str, collections.abc.Iterable],
                       country_code: Union[str, collections.abc.Iterable],
                       anonymity: Union[str, collections.abc.Iterable], https: bool) -> str:
        args = locals()
        filter_str = ""
        for arg in []:
            if arg == "https" and args[arg] == 'any':
                continue
            if args[arg] is not None:
                if arg is not None and isinstance(args[arg], bool):
                    filter_str += f"(self.proxies['{arg}'] == {args[arg]})&"
                if arg is not None and isinstance(args[arg], str):
                    filter_str += f"(self.proxies['{arg}'] == '{args[arg]}') & "
                if arg is not None and isinstance(args[arg], collections.abc.Iterable) and not isinstance(arg,
                                                                                                          (bytes, str)):
                    filter_str += f"(self.proxies['{arg}'].isin({args[arg]})) &"
        if filter_str == "":
            return ""
        filter_str = filter_str[: len(filter_str) - 3] + filter_str[len(filter_str) - 3:].replace("&", "")
        return f"self.proxies[{filter_str}]"


    def find_working_proxy(self) -> dict:
        if self.filtered_df.empty:
            return None
        if self.random:
            for i in range(len(self.filtered_df)):
                random_proxy = self.filtered_df.loc[random.choice(list(self.filtered_df.index))]
                random_proxy, ipaddress = self.series_to_proxy(random_proxy)
                proxy = self.check_if_proxy_is_working(random_proxy)
                if proxy:
                    return proxy
                else:
                    self.filtered_df.drop(ipaddress, inplace=True)
        else:
            for proxy in self.filtered_df.index:
                proxy_inner = self.filtered_df.loc[proxy]
                proxy_inner, ipaddress = self.series_to_proxy(proxy_inner)
                proxy_inner = self.check_if_proxy_is_working(proxy_inner)
                if proxy_inner:
                    return proxy_inner

    def check_if_proxy_is_working(self, proxy) -> dict:
        http_str = 'https' if self.https else 'http'
        try:
            with requests.get(f'{http_str}://www.google.com', proxies=proxy, timeout=self.timeout, stream=True) as r:
                if r.raw.connection.sock:
                    if r.raw.connection.sock.getpeername()[0] == proxy[http_str].split(':')[0]:
                        return proxy
        except Exception:
            return False

    def get(self):

        if self.proxies is None:
            self.get_proxy_list()
        elif time.time() - self.fetched_at >= self.refresh_after:
            self.get_proxy_list()

        if self.prefered_country is not None:
            filter_str = self.get_filter_str(self.prefered_country, self.prefered_country_code, self.anonym, self.https)
        else:
            filter_str = self.get_filter_str(self.country, self.country_code, self.anonym, self.https)

        if filter_str != "":
            exec(f"self.filtered_df = {filter_str}")
        else:
            self.filtered_df = self.proxies

        working_proxy = self.find_working_proxy()
        if working_proxy is not None:
            return working_proxy

        warnings.warn("For the prefered country no working proxies have been found. Checking Countries. If countries is None all countries will be checked")
        if self.prefered_country is not None:
            filter_str = self.get_filter_str(self.country, self.country_code, self.anonym, self.https)
            if filter_str != "":
                exec(f"self.filtered_df = {filter_str}")
            else:
                self.filtered_df = self.proxies
            working_proxy = self.find_working_proxy(self.random, self.timeout, self.filtered_df, self.https)
            if working_proxy is not None:
                return working_proxy


