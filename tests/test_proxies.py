import unittest

from aisexplorer.Proxy import FreeProxy


class TestProxy(unittest.TestCase):
    def test_proxy(self):
        proxy = FreeProxy()
        self.assertIsInstance(proxy, FreeProxy)

    def test_proxy_list(self):
        proxy = FreeProxy()
        proxy.fetch_proxy_list()
        self.assertTrue(not proxy.proxies.empty)

    def test_proxy_list_len(self):
        proxy = FreeProxy()
        proxy.fetch_proxy_list()
        self.assertTrue(len(proxy.proxies) > 0)
