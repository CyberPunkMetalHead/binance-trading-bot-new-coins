from discord_webhook import DiscordWebhook
from notification import NotificationAbstract
from util.types import Order, NotificationSettings, NotificationAuth
from typing import NoReturn, Union
import sys
from telegram import Bot, Chat


class PrettyNotification(NotificationAbstract):
    def __init__(
        self,
        name: str,
        settings: NotificationSettings,
        auth: Union[None, NotificationAuth],
    ):
        self.settings = settings
        if auth is None:
            print("MISSING AUTHENTICATION FOR {}".format(name))
            sys.exit(1)
        self.send_fn = None

    def _format_message(self, order: Order):
        return """
        Broker: {broker}
        Datetime: {datetime}
        Status: {status}
        
        Ticker: {ticker}
        Amount: {amount}
        Price: {price}
        
        """.format(
            broker=order.broker,
            datetime=order.purchase_datetime,
            status=order.status,
            ticker=order.ticker.ticker,
            amount=round(order.size, 4),
            price=round(order.price, 4),
        )

    def _pretty_entry(self, order: Order, *args, **kwargs):
        if "custom" in kwargs and kwargs["custom"] and "comment" in kwargs:
            return kwargs["comment"]
        else:
            msg = """\nNEW POSITION\n"""

            if "comment" in kwargs:
                msg += "\n{comment}\n".format(comment=kwargs["comment"])

            msg += self._format_message(order)
            return msg

    def _pretty_close(self, order: Order, *args, **kwargs):
        if "custom" in kwargs and kwargs["custom"] and "comment" in kwargs:
            return kwargs["comment"]
        else:
            msg = """POSITION CLOSED\n"""

            if "comment" in kwargs:
                msg += "\n{comment}\n".format(comment=kwargs["comment"])

            msg += self._format_message(order)
            return msg

    def _send(self, message: str, *args, **kwargs):
        raise NotImplementedError

    def send_message(self, message: str, *args, **kwargs):
        if self.settings.send_message:
            self._send(message, *args, **kwargs)

    def send_error(self, message: str, *args, **kwargs):
        if self.settings.send_error:
            self._send(message, *args, **kwargs)

    def send_verbose(self, message: str, *args, **kwargs):
        if self.settings.send_verbose:
            self._send(message, *args, **kwargs)

    def send_warning(self, message: str, *args, **kwargs):
        if self.settings.send_warning:
            self._send(message, *args, **kwargs)

    def send_info(self, message: str, *args, **kwargs):
        if self.settings.send_info:
            self._send(message, *args, **kwargs)

    def send_debug(self, message: str, *args, **kwargs):
        if self.settings.send_debug:
            self._send(message, *args, **kwargs)

    def send_entry(self, order: Order, *args, **kwargs):
        if self.settings.send_entry:
            self._send(self._pretty_entry(order, *args, **kwargs))

    def send_close(self, order: Order, *args, **kwargs):
        if self.settings.send_close:
            self._send(self._pretty_close(order, *args, **kwargs))


class DiscordNotification(PrettyNotification):
    def __init__(
        self, settings: NotificationSettings, auth: Union[None, NotificationAuth]
    ) -> NoReturn:
        super().__init__("DISCORD", settings, auth)
        self.send_fn = DiscordWebhook(auth.endpoint)

    def _send(self, message: str, *args, **kwargs):
        self.send_fn.set_content(message)
        self.send_fn.execute()


class TelegramNotification(PrettyNotification):
    def __init__(
        self, settings: NotificationSettings, auth: Union[None, NotificationAuth]
    ) -> NoReturn:
        super().__init__("TELEGRAM", settings, auth)

        self.bot = Bot(auth.endpoint)
        self.chat_id = auth.chat_id
        self.send_fn = Chat(self.chat_id, "private", bot=self.bot)

    def _send(self, message: str, *args, **kwargs):
        self.send_fn.send_message(message)
