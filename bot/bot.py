from broker import Broker
from util import Config
from typing import List, Dict, NoReturn
import logging
from util.types import BrokerType, Ticker, Order, Sold
from util import Util
import traceback

logger = logging.getLogger(__name__)
errLogger = logging.getLogger("error_log")
errLogger.propagate = False


class Bot:
    def __init__(self, broker: BrokerType):
        self.broker = Broker.factory(broker)
        self.config = Config()
        self.config.load_broker_config(self.broker.brokerType)

        self._pending_remove = []

        self.all_tickers = self.broker.get_tickers(self.config.QUOTE_TICKER)
        self.ticker_seen_dict = []
        self.generate_ticker_seen_dict()

        # create / load files
        self.orders: Dict[str, Order] = {}
        self.orders_file = None

        self.sold: Dict[str, Sold] = {}
        self.sold_file = None

        for f in ["orders", "sold"]:
            file = Config.ROOT_DIR.joinpath(f"{self.broker.brokerType}_{f}.json")
            self.__setattr__(f"{f}_file", file)
            if file.exists():
                self.__setattr__(f, Util.load_json(file))

        # Meta info
        self.interval = 0

    async def run_async(self):
        """
        Sells, adjusts TP and SL according to trailing values
        and buys new tickers
        """
        try:
            self.periodic_update()

            # basically the sell block and update TP and SL logic
            if len(self.orders) > 0:
                logger.debug(
                    f"[{self.broker.brokerType}]\tActive Order Tickers: [{self.orders}]"
                )

                for key, stored_order in self.orders.items():
                    self.update(key, stored_order)

            # remove pending removals
            [self.orders.pop(o) for o in self._pending_remove]
            self._pending_remove = []

            # check if new tickers are listed
            new_tickers = self.get_new_tickers()

            if len(new_tickers) > 0:
                logger.info(
                    f"[{self.broker.brokerType}]\tNew tickers detected: {new_tickers}"
                )

                for new_ticker in new_tickers:
                    self.process_new_ticker(new_ticker)
            else:
                logger.debug(f"[{self.broker.brokerType}]\tNo new tickers found..")

            self.interval += 1

        except Exception as e:
            self.save()
            errLogger.error(traceback.format_exc())

        finally:
            self.save()

    def update(self, key, order, **kwargs):
        # This is for testing
        current_price = kwargs.get(
            "current_price", self.broker.get_current_price(order.ticker)
        )

        # if the price is decreasing and is below the stop loss
        if current_price < order.stop_loss:
            self.close_trade(order, current_price, order.price)

        # if the price is increasing and is higher than the old stop-loss maximum, update trailing stop loss
        elif (
            current_price > order.trailing_stop_loss_max
            and self.config.ENABLE_TRAILING_STOP_LOSS
        ):
            self.orders[key] = self.update_trailing_stop_loss(order, current_price)

        # if price is increasing and is higher than the take profit maximum
        elif current_price > order.take_profit:
            self.close_trade(order, current_price, order.price)

        # if the price is decreasing and has fallen below the trailing stop loss minimum
        elif current_price < order.trailing_stop_loss:
            self.close_trade(order, current_price, order.price)

    def periodic_update(self):
        """
        log an update about every LOG_INFO_UPDATE_INTERVAL minutes
        also re-saves files
        """
        if (
            self.interval > 0
            and self.interval
            % (
                (Config.PROGRAM_OPTIONS["LOG_INFO_UPDATE_INTERVAL"] * 60)
                / Config.FREQUENCY_SECONDS
            )
            == 0
        ):
            logger.info(f"[{self.broker.brokerType}] ORDERS UPDATE:\n\t{self.orders}")
            logger.info(f"[{self.broker.brokerType}]\tSaving..")
            self.save()

    def generate_ticker_seen_dict(self) -> NoReturn:
        """
        This method should be used once before starting the loop.
        The value for every ticker detected before the loop is set to True in the ticker_seen_dict.
        All the new tickers detected during the loop will have a value of False.
        """
        ticker_seen_dict = {}
        for ticker in self.all_tickers:
            ticker_seen_dict[ticker.ticker] = True
        self.ticker_seen_dict = ticker_seen_dict

    def get_new_tickers(self) -> List[Ticker]:
        """
        This method checks if there are new tickers listed and returns them in a list.
        The value of the new tickers in ticker_seen_dict will be set to True to make them not get detected again.
        """
        new_tickers = []
        logger.debug(f"[{self.broker.brokerType}]\tGetting all tickers..")
        all_tickers_recheck = self.broker.get_tickers(self.config.QUOTE_TICKER)

        if len(all_tickers_recheck) != self.ticker_seen_dict:
            new_tickers = [
                i for i in all_tickers_recheck if i.ticker not in self.ticker_seen_dict
            ]

            for new_ticker in new_tickers:
                self.ticker_seen_dict[new_ticker.ticker] = True

        return new_tickers

    def update_trailing_stop_loss(self, order: Order, current_price: float) -> Order:

        # increase as absolute value for TP
        order.trailing_stop_loss_max = max(current_price, order.price)
        order.trailing_stop_loss = Util.percent_change(
            order.trailing_stop_loss_max, -self.config.TRAILING_STOP_LOSS_PERCENT
        )

        logger.info(
            f"[{self.broker.brokerType}]\t[{order.ticker.ticker}] Updated:\n\tTrailing Stop-Loss: {round(order.trailing_stop_loss, 3)}"
        )

        return order

    def close_trade(self, order: Order, current_price: float, stored_price: float):

        sell: Order = self.broker.place_order(
            self.config,
            ticker=order.ticker,
            side="sell",
            size=order.size,
            current_price=current_price,
        )
        if Config.TEST:
            logger.info(
                f"[{self.broker.brokerType}]\t[TEST MODE] - Sold [{order.ticker.ticker}] at {(current_price - stored_price) / stored_price * 100}"
            )
        else:
            logger.info(
                f"[{self.broker.brokerType}]\tSold [{order.ticker.ticker}] at {(current_price - stored_price) / stored_price * 100}"
            )

        # pending remove order from json file
        self._pending_remove.append(order.ticker.ticker)

        # store sold trades data
        self.sold[order.ticker.ticker] = Sold(
            ticker=order.ticker,
            purchase_datetime=order.purchase_datetime,
            price=sell.price,
            side=sell.side,
            size=sell.size,
            type=sell.type,
            status=sell.status,
            take_profit=sell.take_profit,
            stop_loss=sell.stop_loss,
            trailing_stop_loss_max=sell.trailing_stop_loss_max,
            trailing_stop_loss=sell.trailing_stop_loss,
            profit=current_price - stored_price,
            profit_percent=(current_price - stored_price) / stored_price * 100,
            sold_datetime=sell.purchase_datetime,
        )

    def process_new_ticker(self, new_ticker: Ticker):
        # buy if the ticker hasn't already been bought
        if (
            new_ticker.ticker not in self.orders
            and self.config.QUOTE_TICKER in new_ticker.quote_ticker
        ):
            logger.info(
                f"[{self.broker.brokerType}]\tPreparing to buy {new_ticker.ticker}"
            )

            price = self.broker.get_current_price(new_ticker)
            size = self.broker.convert_size(
                config=self.config, ticker=new_ticker, price=price
            )

            try:

                logger.info(
                    f"[{self.broker.brokerType}]\tPlacing [{'TEST' if self.config.TEST else 'LIVE'}] Order.."
                )
                order = self.broker.place_order(
                    self.config, ticker=new_ticker, size=size, side="BUY"
                )
                self.orders[new_ticker.ticker] = order

            except Exception as e:
                logger.error(e)

            else:
                logger.info(
                    f"[{self.broker.brokerType}]\tOrder created with {size} on {new_ticker.ticker}"
                )
        else:
            logger.error(
                f"[{self.broker.brokerType}]\tNew new_ticker detected, but {new_ticker.ticker} is currently in "
                f"portfolio, or {self.config.QUOTE_TICKER} does not match"
            )

    def save(self):
        Util.dump_json(self.orders_file, self.orders)
        Util.dump_json(self.sold_file, self.sold)
