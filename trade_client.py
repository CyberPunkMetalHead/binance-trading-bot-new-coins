from auth.binance_auth import *
from binance.enums import *

client = load_binance_creds('auth/auth.yml')

def get_price(coin):
     return client.get_ticker(symbol=coin)['lastPrice']


def convert_volume(coin, quantity, last_price):
    """Converts the volume given in QUANTITY from USDT to the each coin's volume"""

    try:
        info = client.get_symbol_info(coin)
        step_size = info['filters'][2]['stepSize']
        lot_size = {coin:step_size.index('1') - 1}

        if lot_size[coin] < 0:
            lot_size[coin] = 0

    except:
        print("Ran except block for lot size")
        lot_size = {coin:0}
        pass

    print(lot_size[coin])
    # calculate the volume in coin from QUANTITY in USDT (default)
    volume = float(quantity / float(last_price))

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


def create_order(coin, amount, action):
    """
    Creates simple buy order and returns the order
    """
    return client.create_margin_order(
        symbol = coin,
        side = action,
        type = 'MARKET',
        quantity = amount
    )
