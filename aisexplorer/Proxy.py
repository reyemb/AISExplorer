import random
import sys
import time
import lxml.html as lh
import requests
import pandas as pd
import collections
import warnings


def check_valid_ip(string):
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


def get_filter_str(country, anonymity, https):
    args = locals()
    filter_str = ""
    for arg in args:
        if args[arg] is not None:
            if arg is not None and isinstance(arg, str):
                filter_str += f"(self.proxies['{arg}'] == {args[arg]}) & "
            if arg is not None and isinstance(arg, collections.abc.Iterable) and not isinstance(arg, (bytes, str)):
                filter_str += f"(self.proxies['{arg}'].isin({args[arg]}) &"
    if filter_str == "":
        return ""
    filter_str = filter_str[: len(filter_str)- 3] + filter_str[len(filter_str)-3:].replace("&", "")
    return f"self.proxies[{filter_str}]"


def check_if_proxy_is_working(proxy, timeout, https):
    try:
        http_str = 'https' if https else 'http'
        proxy_set = {
            http_str: f"{proxy.name}:{proxy['port']}"
        }
        with requests.get(f'{http_str}://www.google.com', proxies=proxy_set, timeout=timeout, stream=True) as r:
            if r.raw.connection.sock:
                if r.raw.connection.sock.getpeername()[0] == proxy_set[http_str].split(':')[0]:
                    return proxy_set
    except Exception as e:
        return False


def find_working_proxy(random_input, timeout, filtered_df, https):
    if filtered_df.empty:
        return None
    if random_input:
        for i in range(len(filtered_df)):
            random_proxy = filtered_df.loc[random.choice(list(filtered_df.index))]
            proxy = check_if_proxy_is_working(random_proxy, timeout, https)
            if proxy:
                return proxy
            else:
                filtered_df.drop(random_proxy.name, inplace=True)
    else:
        for proxy in filtered_df.index:
            proxy_inner = check_if_proxy_is_working(proxy, timeout, https)
            if check_if_proxy_is_working(filtered_df.loc[proxy], timeout):
                return proxy_inner


dict_str = {
    'yes': True,
    '': False,
    'no': False,
}


def convert_str_to_bool(string):
    return dict_str.get(string)


list_columns_to_clean = ['google', 'https']


def clean_dataframe(df):
    for column in list_columns_to_clean:
        if column in df.columns:
            df[column] = df[column].apply(lambda x: convert_str_to_bool(x))
    return df


class FreeProxy:
    def __init__(self, country: str = None, timeout=0.5, anonym=None, https=True, rand=True,
                 prefered_country: str = None, refresh_after=1800):
        self.country = country
        self.timeout = timeout
        self.anonym = anonym
        self.https = https
        self.random = rand
        self.proxies = None
        self.prefered_country = prefered_country
        self.fetched_at = None
        self.refresh_after = refresh_after
        self.filtered_df = None

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

    def get(self):

        if self.proxies is None:
            self.get_proxy_list()
        elif time.time() - self.fetched_at >= self.refresh_after:
            self.get_proxy_list()

        if self.prefered_country is not None:
            filter_str = get_filter_str(self.prefered_country, self.anonym, self.https)
        else:
            filter_str = get_filter_str(self.country, self.anonym, self.https)

        if filter_str != "":
            exec(f"self.filtered_df = {filter_str}")
        else:
            self.filtered_df = self.proxies

        working_proxy = find_working_proxy(self.random, self.timeout, self.filtered_df, self.https)
        if working_proxy is not None:
            return working_proxy

        warnings.warn("For the prefered country no working proxies have been found. Checking Countries. If countries is None all countries will be checked")
        if self.prefered_country is not None:
            filter_str = get_filter_str(self.country, self.anonym, self.https)
            if filter_str != "":
                exec(f"self.filtered_df = {filter_str}")
            else:
                self.filtered_df = self.proxies
            working_proxy = find_working_proxy(self.random, self.timeout, self.filtered_df)
            if working_proxy is not None:
                return working_proxy


