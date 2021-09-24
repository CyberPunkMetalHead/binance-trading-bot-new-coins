from typing import Union, Optional
from datetime import datetime
from pydantic import BaseModel

BROKERS = ["BINANCE", "FTX"]

BrokerType = Union["FTX", "BINANCE"]
ActionType = Union["Buy", "Sell"]
NotificationType = Union["COMMAND_LINE", "DISCORD", "TELEGRAM", "EMAIL"]


class NotificationSettings(BaseModel):
    send_message: Optional[bool] = True

    send_error: Optional[bool] = True
    send_verbose: Optional[bool] = False
    send_warning: Optional[bool] = False
    send_info: Optional[bool] = False
    send_debug: Optional[bool] = False

    send_entry: Optional[bool] = True
    send_close: Optional[bool] = True


class NotificationAuth(BaseModel):
    endpoint: Optional[str] = None
    chat_id: Optional[int] = None


class Notification(BaseModel):
    service: str
    enabled: bool
    settings: Optional[NotificationSettings] = None
    auth: Optional[NotificationAuth] = None


class Ticker(BaseModel):
    ticker: str
    base_ticker: str
    quote_ticker: str


class Order(BaseModel):
    broker: str
    ticker: Ticker
    purchase_datetime: datetime
    price: float
    side: str
    size: float
    type: str
    status: str

    take_profit: float
    stop_loss: float

    trailing_stop_loss_max: float
    trailing_stop_loss: float


class Sold(Order):
    profit: float
    profit_percent: float
    sold_datetime: datetime
