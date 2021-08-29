from auth.binance_auth import load_binance_creds
import logging
from typing import Dict
from util.types import ActionType
from datetime import datetime
import os
from util.constants import ROOT_DIR

client = load_binance_creds(os.path.join(ROOT_DIR, 'auth/auth.yml'))
logger = logging.getLogger(__name__)


def get_price_by_symbol(coin: str) -> float:
    return float(client.get_ticker(symbol=coin)['lastPrice'])


def convert_volume(coin: str, quantity: float, last_price: float):
    """Converts the volume given in QUANTITY from USDT to the each coin's volume"""

    try:
        info = client.get_symbol_info(coin)
        step_size = info['filters'][2]['stepSize']
        lot_size = {coin: step_size.index('1') - 1}

        if lot_size[coin] < 0:
            lot_size[coin] = 0

    except Exception as e:
        logger.error("Ran except block for lot size")
        lot_size = {coin: 0}
        pass

    logger.info(lot_size[coin])
    # calculate the volume in coin from QUANTITY in USDT (default)
    volume = quantity / last_price

    # define the volume with the correct step size
    if coin not in lot_size:
        volume = float('{:.1f}'.format(volume))

    else:
        # if lot size has 0 decimal points, make the volume an integer
        if lot_size[coin] == 0:
            volume = int(volume)
        else:
            volume = float('{:.{}f}'.format(volume, lot_size[coin]))

    return volume


def create_order(coin: str, amount: float, action: ActionType, test_mode=False) -> Dict:
    """
    Creates simple buy order and returns the order
    """
    if test_mode:
        price = get_price_by_symbol(coin)
        return {'symbol': coin, 'orderId': 999, 'clientOrderId': 'N/A', 'transactTime': datetime.now().timestamp(),
                'price': price, 'origQty': amount, 'status': 'TEST_MODE', 'timeInForce': 'GTC', 'type': "MARKET",
                'side': action}
    else:
        return client.create_order(
            symbol=coin,
            side=action,
            type='MARKET',
            quantity=amount
        )
