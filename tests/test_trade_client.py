from unittest import TestCase
from trade_client import *


class Test(TestCase):
    def test_get_price_by_symbol(self):
        price = get_price_by_symbol('BTCUSDT')
        print(price)
        self.assertTrue(float(price) > 0)

    def test_convert_volume(self):
        coin = "BTCUSDT"
        vol = convert_volume(coin, 100.0, get_price_by_symbol(coin))
        print(vol)

    def test_create_order(self):
        coin = "BTCUSDT"
        resp = create_order(coin, 1.0, "BUY", True)
        self.assertTrue(resp['price'] > 0)
