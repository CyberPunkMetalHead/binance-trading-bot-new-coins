from unittest import TestCase
from bot import Bot
from util.types import Order, Ticker, Notification, NotificationAuth
from util import Util
from util import Config
import logging
from notification import NotificationService
from time import sleep

# setup logging
Util.setup_logging(name="new-coin-bot", level="DEBUG")

logger = logging.getLogger(__name__)


class TestBot(TestCase):
    def setUp(self) -> None:
        # Config.load_global_config()
        self.FTX = Bot("FTX")
        self.Binance = Bot("BINANCE")
        self.maxDiff = None
        Config.TEST = True

        self.FTX.config.STOP_LOSS_PERCENT = 3
        self.FTX.config.TAKE_PROFIT_PERCENT = 3
        self.FTX.config.TRAILING_STOP_LOSS_PERCENT = 2
        self.FTX.config.TRAILING_STOP_LOSS_PERCENT = 2

        self.Binance.config.STOP_LOSS_PERCENT = 3
        self.Binance.config.TAKE_PROFIT_PERCENT = 3
        self.Binance.config.TRAILING_STOP_LOSS_PERCENT = 2
        self.Binance.config.TRAILING_STOP_LOSS_PERCENT = 2

    def test_get_new_tickers(self):
        expected = len(self.FTX.ticker_seen_dict)
        self.FTX.ticker_seen_dict = {"BTC/USDT": True}
        actual = self.FTX.get_new_tickers()
        self.assertEqual(len(actual), expected - 1)

        expected = len(self.Binance.ticker_seen_dict)
        self.Binance.ticker_seen_dict = {"BTCUSDT": True}
        actual = self.Binance.get_new_tickers()
        self.assertEqual(len(actual), expected - 1)

    def test_purchase(self):
        tickers, ticker_dict = self.FTX.get_starting_tickers()
        self.FTX.all_tickers = [t for t in tickers if t.ticker != "BTC/USDT"]
        ticker_dict.pop("BTC/USDT")
        self.FTX.ticker_seen_dict = ticker_dict
        new_tickers = self.FTX.get_new_tickers()

        for new_ticker in new_tickers:
            self.FTX.process_new_ticker(new_ticker)

        self.assertTrue("BTC/USDT" in self.FTX.orders)

        tickers, ticker_dict = self.Binance.get_starting_tickers()
        self.Binance.all_tickers = [t for t in tickers if t.ticker != "BTCUSDT"]
        ticker_dict.pop("BTCUSDT")
        self.Binance.ticker_seen_dict = ticker_dict
        new_tickers = self.Binance.get_new_tickers()

        for new_ticker in new_tickers:
            self.Binance.process_new_ticker(new_ticker)

        self.assertTrue("BTCUSDT" in self.Binance.orders)

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
        self.FTX.config.TRAILING_STOP_LOSS_PERCENT = 2

        for key, value in self.FTX.orders.items():
            self.FTX.update(key, value, current_price=60000)

            expected = Util.load_pickle(
                Config.TEST_DIR.joinpath("FTX_order_test_update_above_max_expected")
            )
            self.assertDictEqual(expected, self.FTX.orders)

    def test_update_above_tp(self):
        self.FTX.config.ENABLE_TRAILING_STOP_LOSS = False

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

    def test_notifications(self):

        NotificationService.DEFAULT_SETTINGS = {
            "SEND_MESSAGE": True,
            "SEND_ERROR": True,
            "SEND_VERBOSE": True,
            "SEND_WARNING": True,
            "SEND_INFO": True,
            "SEND_DEBUG": True,
            "SEND_ENTRY": True,
            "SEND_CLOSE": True,
        }
        Config.load_global_config()

        Config.NOTIFICATION_SERVICE.send_message("send_message test")
        sleep(0.1)
        Config.NOTIFICATION_SERVICE.send_error("send_error test")
        sleep(0.1)
        Config.NOTIFICATION_SERVICE.send_verbose("send_verbose test")
        sleep(0.1)
        Config.NOTIFICATION_SERVICE.send_warning("send_warning test")
        sleep(0.1)
        Config.NOTIFICATION_SERVICE.send_info("send_info test")
        sleep(0.1)
        Config.NOTIFICATION_SERVICE.send_debug("send_debug test")
        sleep(0.1)

        tickers, ticker_dict = self.FTX.get_starting_tickers()
        self.FTX.all_tickers = [t for t in tickers if t.ticker != "BTC/USDT"]
        ticker_dict.pop("BTC/USDT")
        self.FTX.ticker_seen_dict = ticker_dict
        new_tickers = self.FTX.get_new_tickers()

        for new_ticker in new_tickers:
            self.FTX.process_new_ticker(new_ticker)

        Config.NOTIFICATION_SERVICE.send_entry(self.FTX.orders["BTC/USDT"])
        sleep(0.1)
        Config.NOTIFICATION_SERVICE.send_close(self.FTX.orders["BTC/USDT"])
        sleep(0.1)
        Config.NOTIFICATION_SERVICE.send_entry(
            self.FTX.orders["BTC/USDT"], custom=True, comment="Custom Entry Comment"
        )

    def test_github_failed(self):
        Config.load_global_config()
        new_tickers = [Ticker(ticker='YGGUSDT', base_ticker='YGG', quote_ticker='USDT'), Ticker(ticker='SYSUSDT', base_ticker='SYS', quote_ticker='USDT')]
        for new_ticker in new_tickers:
            self.Binance.process_new_ticker(new_ticker)



    # LEAVE OFF, PLEASE DON'T SPAM MY ACCOUNT :)

    # def test_pipedream(self):
    #     tickers, ticker_dict = self.FTX.get_starting_tickers()
    #     self.FTX.all_tickers = [t for t in tickers if t.ticker != 'BTC/USDT']
    #     ticker_dict.pop('BTC/USDT')
    #     self.FTX.ticker_seen_dict = ticker_dict
    #     new_tickers = self.FTX.get_new_tickers()
    #
    #     for new_ticker in new_tickers:
    #         self.FTX.process_new_ticker(new_ticker)
    #
    #     resp = Util.post_pipedream(self.FTX.orders['BTC/USDT'])
    #     self.assertTrue(resp.status_code == 200)
