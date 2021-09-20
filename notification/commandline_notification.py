from notification import NotificationAbstract
from util.types import Order
from typing import NoReturn
import logging

logger = logging.getLogger(__name__)
errLogger = logging.getLogger("error_log")
verboseLogger = logging.getLogger("verbose_log")
errLogger.propagate = False


class CommandlineNotification(NotificationAbstract):
    def __init__(self):
        super().__init__()

    def _default_msg_start(self, order: Order) -> str:
        return "[{broker} - {ticker}]\t".format(
            broker=order.broker, ticker=order.ticker.ticker
        )

    def _default_action(self, order: Order, *args, **kwargs) -> str:
        if "custom" in kwargs and kwargs["custom"] and "comment" in kwargs:
            logger.info(kwargs["comment"])
        else:
            msg = self._default_msg_start(order)

            if "comment" in kwargs:
                msg += " - {comment} - ".format(comment=kwargs["comment"])
            return msg

    def _send(self, message: str, *args, **kwargs) -> NoReturn:
        raise NotImplementedError

    def send_message(self, message: str, *args, **kwargs) -> NoReturn:
        logger.warning(message, *args, **kwargs)

    def send_error(self, message: str, *args, **kwargs) -> NoReturn:
        logger.error(message, *args, **kwargs)
        errLogger.error(message, *args, **kwargs)

    def send_verbose(self, message: str, *args, **kwargs) -> NoReturn:
        verboseLogger.debug(message, *args, **kwargs)

    def send_warning(self, message: str, *args, **kwargs) -> NoReturn:
        verboseLogger.warning(message, *args, **kwargs)

    def send_info(self, message: str, *args, **kwargs) -> NoReturn:
        logger.info(message, *args, *kwargs)

    def send_debug(self, message: str, *args, **kwargs) -> NoReturn:
        logger.debug(message, *args, **kwargs)

    def send_entry(self, order: Order, *args, **kwargs) -> NoReturn:
        self._default_action(order, *args, **kwargs)

    def send_close(self, order: Order, *args, **kwargs) -> NoReturn:
        self._default_action(order, *args, **kwargs)
