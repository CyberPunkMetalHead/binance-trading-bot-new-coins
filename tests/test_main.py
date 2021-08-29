from unittest import TestCase
from main import get_all_coins, get_price, get_new_coins


class Test(TestCase):
    def test_get_all_coins(self):
        try:
            resp = get_all_coins()
            print(resp)
            self.assertTrue(len(resp) > 0)
        except Exception as e:
            print(e)
            self.fail()

    def test_get_new_coins(self):
        all_coins = [{'symbol': 'ETHBTC', 'price': '0.06642100'}, {'symbol': 'LTCBTC', 'price': '0.00365700'}]
        new_coins, all_coins_recheck = get_new_coins(all_coins)
        self.assertTrue(len(new_coins) > 0)
        self.assertTrue(len(all_coins_recheck) > 0)

    def test_get_price(self):
        price = get_price('BTC', 'USDT')
        print(price)
        self.assertGreater(price, 0)
