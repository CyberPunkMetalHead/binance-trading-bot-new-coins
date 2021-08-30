from abc import ABC, abstractmethod
from typing import Dict, Any, NoReturn, List
from ftx.api import FtxClient
from binance.client import Client as BinanceClient
from datetime import datetime
import logging
from typing import Union
from util.types import BrokerType, Ticker, Order
from util.exceptions import *
from util import Config, Util
from dateutil.parser import parse
import yaml

logger = logging.getLogger(__name__)
errLogger = logging.getLogger("error_log")
errLogger.propagate = False


class Broker(ABC):
    def __init__(self):
        self.brokerType = None

    @staticmethod
    def factory(broker: BrokerType, subaccount: Union[str, None] = None) -> Any:
        with open(Config.AUTH_DIR.joinpath("auth.yml")) as file:
            auth = yaml.load(file, Loader=yaml.FullLoader)

            if broker == "FTX":
                return FTX(
                    subaccount=subaccount,
                    key=auth["FTX"]["key"],
                    secret=auth["FTX"]["secret"],
                )
            if broker == "BINANCE":
                # TODO - SUBACCOUNTS FOR BINANCE IS NOT IMPLEMENTED YET
                return Binance(
                    subaccount="",
                    key=auth["BINANCE"]["key"],
                    secret=auth["BINANCE"]["secret"],
                )

    @abstractmethod
    def get_tickers(self, quote_ticker: str) -> List[Ticker]:
        """
        Returns all coins from Broker
        """
        raise NotImplementedError

    @abstractmethod
    def get_current_price(self, ticker: Ticker) -> float:
        """
        Get the current price for a coin
        """
        raise NotImplementedError

    @abstractmethod
    def place_order(self, config: Config, *args, **kwargs) -> Order:
        raise NotImplementedError

    @abstractmethod
    def convert_size(self, config: Config, ticker: Ticker, price: float) -> float:
        raise NotImplementedError


class FTX(FtxClient, Broker):
    def __init__(self, subaccount: str, key: str, secret: str) -> NoReturn:
        self.brokerType = "FTX"

        super().__init__(
            api_key=key,
            api_secret=secret,
            subaccount_name=subaccount,
        )

    def get_tickers(self, quote_ticker: str) -> List[Ticker]:
        api_resp = super(FTX, self).get_markets()
        resp = []
        for ticker in api_resp:
            if (
                ticker["type"] == "spot"
                and ticker["enabled"]
                and ticker["quoteCurrency"] == quote_ticker
            ):
                if ticker["type"] == "spot" and ticker["enabled"]:
                    resp.append(
                        Ticker(
                            ticker=ticker["name"],
                            base_ticker=ticker["baseCurrency"],
                            quote_ticker=ticker["quoteCurrency"],
                        )
                    )
        return resp

    @FtxClient.authentication_required
    def get_current_price(self, ticker: Ticker):
        logger.debug("Getting latest price for [{}]".format(ticker.ticker))
        try:
            resp = float(self.get_market(market=ticker.ticker)["last"])

            if resp is None:
                raise GetPriceNoneResponse("None Response from Get Price")
            logger.info("FTX Price - {} {}".format(ticker.ticker, round(resp, 4)))
            return resp
        except LookupError as e:
            pass

    @FtxClient.authentication_required
    def place_order(self, config: Config, *args, **kwargs) -> Order:
        if Config.TEST:
            price = kwargs.get(
                "current_price", self.get_current_price(kwargs["ticker"])
            )
            return Order(
                ticker=kwargs["ticker"],
                purchase_datetime=datetime.now(),
                price=price,
                side=kwargs["side"],
                size=kwargs["size"],
                type="market",
                status="TEST_MODE",
                take_profit=Util.percent_change(price, config.TAKE_PROFIT_PERCENT),
                stop_loss=Util.percent_change(price, -config.STOP_LOSS_PERCENT),
                trailing_stop_loss_max=float("-inf"),
                trailing_stop_loss=Util.percent_change(
                    price, -config.TRAILING_STOP_LOSS_PERCENT
                ),
            )

        else:
            kwargs["market"] = kwargs["ticker"]
            del kwargs["ticker"]
            api_resp = super(FTX, self).place_order(*args, *kwargs)
            return Order(
                ticker=kwargs["ticker"],
                purchase_datetime=parse(api_resp["createdAt"]),
                price=api_resp["price"],
                side=api_resp["side"],
                size=api_resp["size"],
                type="market",
                status="LIVE",
                take_profit=Util.percent_change(
                    api_resp["price"], config.TAKE_PROFIT_PERCENT
                ),
                stop_loss=Util.percent_change(
                    api_resp["price"], -config.STOP_LOSS_PERCENT
                ),
                trailing_stop_loss_max=float("-inf"),
                trailing_stop_loss=Util.percent_change(
                    api_resp["price"], -config.TRAILING_STOP_LOSS_PERCENT
                ),
            )

    def convert_size(self, config: Config, ticker: Ticker, price: float) -> float:
        size = config.QUANTITY / price
        return size


class Binance(BinanceClient, Broker):
    def __init__(self, subaccount: str, key: str, secret: str) -> NoReturn:
        self.brokerType = "BINANCE"

        super().__init__(api_key=key, api_secret=secret)

    def get_current_price(self, ticker: Ticker) -> float:
        logger.debug("Getting latest price for [{}]".format(ticker))
        return float(self.futures_mark_price(symbol=ticker.ticker)["markPrice"])

    def place_order(self, config: Config, *args, **kwargs) -> Order:
        kwargs["symbol"] = kwargs["ticker"].ticker
        kwargs["type"] = "market"
        kwargs['quantity'] = kwargs['size']
        params = {}

        for p in ['quantity', 'side', 'symbol', 'type']:
            params[p] = kwargs[p]

        if Config.TEST:
            # does not return anything.  No error mean request was good.
            api_resp = super(Binance, self).create_test_order(**params)
            price = self.get_current_price(kwargs['ticker'])
            return Order(
                ticker=kwargs["ticker"],
                purchase_datetime=datetime.now(),
                price=price,
                side=kwargs["side"],
                size=kwargs["size"],
                type="market",
                status="TEST_MODE",
                take_profit=Util.percent_change(price, config.TAKE_PROFIT_PERCENT),
                stop_loss=Util.percent_change(price, -config.STOP_LOSS_PERCENT),
                trailing_stop_loss_max=float("-inf"),
                trailing_stop_loss=Util.percent_change(
                    price, -config.TRAILING_STOP_LOSS_PERCENT
                ),
            )
        else:
            api_resp = super(Binance, self).create_order(**params)
            return Order(
                ticker=kwargs["symbol"],
                purchase_datetime=parse(api_resp["transactTime"]),
                price=api_resp["price"],
                side=api_resp["side"],
                size=api_resp["executedQty"],
                type="market",
                status="TEST_MODE" if Config.TEST else "LIVE",
                take_profit=Util.percent_change(
                    api_resp["price"], config.TAKE_PROFIT_PERCENT
                ),
                stop_loss=Util.percent_change(api_resp["price"], -config.STOP_LOSS_PERCENT),
                trailing_stop_loss_max=float("-inf"),
                trailing_stop_loss=Util.percent_change(
                    api_resp["price"], -config.TRAILING_STOP_LOSS_PERCENT
                ),
            )



    def get_tickers(self, quote_ticker: str) -> List[Ticker]:
        api_resp = super(Binance, self).get_exchange_info()

        resp = []
        for ticker in api_resp["symbols"]:
            if ticker["isSpotTradingAllowed"] and ticker["quoteAsset"] == quote_ticker:
                resp.append(
                    Ticker(
                        ticker=ticker["symbol"],
                        base_ticker=ticker["baseAsset"],
                        quote_ticker=ticker["quoteAsset"],
                    )
                )

        return resp

    def convert_size(self, config: Config, ticker: Ticker, price: float) -> float:

        info = super(Binance, self).get_symbol_info(symbol=ticker.ticker)
        step_size = info["filters"][2]["stepSize"]
        lot_size = step_size.index("1") - 1
        lot_size = max(lot_size, 0)

        # calculate the volume in coin from QUANTITY in USDT (default)
        size = config.QUANTITY / price

        # if lot size has 0 decimal points, make the volume an integer
        if lot_size == 0:
            size = int(size)
        else:
            size = float("{:.{}f}".format(size, lot_size))

        return size
