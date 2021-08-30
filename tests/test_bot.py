from unittest import TestCase
from bot import Bot
from util.types import Order, Ticker
from util import Util
from util import Config


class TestBot(TestCase):
    def setUp(self) -> None:
        self.FTX = Bot("FTX")
        self.Binance = Bot("BINANCE")
        self.maxDiff = None
        Config.TEST = True

    def test_get_new_tickers(self):
        expected = len(self.FTX.ticker_seen_dict)
        self.FTX.ticker_seen_dict = {"BTC/USDT": True}
        actual = self.FTX.get_new_tickers()
        self.assertEqual(len(actual), expected - 1)

        expected = len(self.Binance.ticker_seen_dict)
        self.Binance.ticker_seen_dict = {"BTCUSDT": True}
        actual = self.Binance.get_new_tickers()
        self.assertEqual(len(actual), expected - 1)

    def test_convert_size(self):
        ticker = Ticker(ticker="BTC/USDT", base_ticker="BTC", quote_ticker="USDT")

        actual = self.FTX.broker.convert_size(
            config=self.FTX.config, ticker=ticker, price=40000
        )
        self.assertEqual(actual, 0.00075)

        actual = self.FTX.broker.convert_size(
            config=self.FTX.config, ticker=ticker, price=0.008675309
        )
        self.assertEqual(actual, 3458.0900807106696)

        ticker = Ticker(ticker="BTCUSDT", base_ticker="BTC", quote_ticker="USDT")
        actual = self.Binance.broker.convert_size(
            self.Binance.config, ticker=ticker, price=48672.73020676
        )
        self.assertEqual(actual, 0.00062)

    def test_process_new_ticker(self):
        self.FTX.ticker_seen_dict = {}
        ticker = Ticker(ticker="BTC/USDT", base_ticker="BTC", quote_ticker="USDT")
        self.FTX.process_new_ticker(ticker)

        self.Binance.ticker_seen_dict = {}
        ticker = Ticker(ticker="BTCUSDT", base_ticker="BTC", quote_ticker="USDT")
        self.Binance.process_new_ticker(ticker)
        pass

    def test_update_below_sl(self):
        self.FTX.orders = Util.load_pickle(Config.TEST_DIR.joinpath("FTX_order_test"))

        for key, value in self.FTX.orders.items():
            self.FTX.update(key, value, current_price=30000)

            expected = Util.load_pickle(
                Config.TEST_DIR.joinpath("FTX_order_test_update_below_sl_expected")
            )
            expected["BTC/USDT"].sold_datetime = self.FTX.sold["BTC/USDT"].sold_datetime
            self.assertDictEqual(expected, self.FTX.sold)

    def test_update_above_max(self):
        self.FTX.orders = Util.load_pickle(Config.TEST_DIR.joinpath("FTX_order_test"))

        for key, value in self.FTX.orders.items():
            self.FTX.update(key, value, current_price=60000)

            expected = Util.load_pickle(
                Config.TEST_DIR.joinpath("FTX_order_test_update_above_max_expected")
            )
            self.assertDictEqual(expected, self.FTX.orders)

    def test_update_above_tp(self):
        self.FTX.config.ENABLE_TRAILING_STOP_LOSS = False
        self.FTX.config.TAKE_PROFIT_PERCENT = 20
        self.FTX.orders = Util.load_pickle(
            Config.TEST_DIR.joinpath("FTX_order_test_tsl_off")
        )

        for key, value in self.FTX.orders.items():
            self.FTX.update(key, value, current_price=60000)

            expected = Util.load_pickle(
                Config.TEST_DIR.joinpath("FTX_order_test_update_above_tp_expected")
            )
            expected["BTC/USDT"].sold_datetime = self.FTX.sold["BTC/USDT"].sold_datetime
            self.assertDictEqual(expected, self.FTX.sold)

    def test_update_below_tsl(self):
        self.FTX.orders = Util.load_pickle(Config.TEST_DIR.joinpath("FTX_order_test"))

        for key, value in self.FTX.orders.items():
            self.FTX.update(key, value, current_price=60000)
            self.FTX.update(key, value, current_price=25000)

            expected = Util.load_pickle(
                Config.TEST_DIR.joinpath("FTX_order_test_update_below_tsl_expected")
            )
            expected["BTC/USDT"].sold_datetime = self.FTX.sold["BTC/USDT"].sold_datetime
            self.assertDictEqual(expected, self.FTX.sold)
