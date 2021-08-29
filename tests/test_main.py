from unittest import TestCase
from main import get_all_coins, get_price, get_new_coins, generate_coin_seen_dict


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
        all_coins_dict = generate_coin_seen_dict(all_coins)
        new_coins = get_new_coins(all_coins_dict)
        self.assertTrue(len(new_coins) > 0)

    def test_get_price(self):
        price = get_price('BTC', 'USDT')
        print(price)
        self.assertGreater(price, 0)

    def test_generate_coin_seen_dict(self):
        all_coins = get_all_coins()
        result = generate_coin_seen_dict(all_coins)
        self.assertTrue(result['BTCUSDT'] is True)
