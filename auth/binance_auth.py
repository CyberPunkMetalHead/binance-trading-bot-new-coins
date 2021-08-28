import yaml

from binance.client import Client
from binance.exceptions import BinanceAPIException


def load_binance_creds(file):
    with open(file) as file:
        auth = yaml.load(file, Loader=yaml.FullLoader)

    return Client(auth['binance_api'], auth['binance_secret'])
