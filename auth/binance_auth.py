import yaml

from binance.client import Client
from binance.exceptions import BinanceAPIException


def load_binance_creds(file):
    with open(file) as file:
        auth = yaml.load(file, Loader=yaml.FullLoader)

    return Client(api_key=auth['binance_api'], api_secret=auth['binance_secret'], tld=auth['binance_tld'])
