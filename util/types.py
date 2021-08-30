from typing import Union, Optional
from datetime import datetime
from pydantic import BaseModel

BROKERS = ["BINANCE", "FTX"]

BrokerType = Union['FTX', 'BINANCE']
ActionType = Union["Buy", "Sell"]


class Ticker(BaseModel):
    ticker: str
    base_ticker: str
    quote_ticker: str


class Order(BaseModel):
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
