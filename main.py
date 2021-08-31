from store_order import *
from load_config import *
from trade_client import *

from collections import defaultdict
from datetime import datetime
from time import sleep

import os.path


# loads local configuration
config = load_config('config.yml')



def get_all_coins():
    """
    Returns all coins from Binance
    """
    return client.get_all_tickers()


def generate_coin_seen_dict(all_coins):
    """
    This method should be used once before starting the loop.
    The value for every coin detected before the loop is set to True in the coin_seen_dict.
    All the new coins detected during the loop will have a value of False.
    """
    coin_seen_dict = defaultdict(bool)
    for old_coin in all_coins:
        coin_seen_dict[old_coin['symbol']] = True
    return coin_seen_dict


def get_new_coins(coin_seen_dict):
    """
    This method checks if there are new coins listed and returns them in a list.
    The value of the new coins in coin_seen_dict will be set to True to make them not get detected again.
    """
    result = []
    all_coins_recheck = get_all_coins()

    for new_coin in all_coins_recheck:
        if not coin_seen_dict[new_coin['symbol']]:
            result += [new_coin]
            # this line ensures the new coin isn't detected again
            coin_seen_dict[new_coin['symbol']] = True

    return result


def get_price(coin, pairing):
    """
    Get the latest price for a coin
    """
    return client.get_ticker(symbol=coin+pairing)['lastPrice']


def handle_new_coin(new_coins, qty, order, pairing, tp, sl, test_mode):
    """Handle new coin logic."""
    print(f'New coins detected: {new_coins}')
    
    for coin in new_coins:
    
        # buy if the coin hasn't already been bought
        if coin['symbol'] not in order and pairing in coin['symbol']:
            symbol_only = coin['symbol'].split(pairing)[0]
            print(f"Preparing to buy {coin['symbol']}")
    
            price = get_price(symbol_only, pairing)
            volume = convert_volume(coin['symbol'], qty, price)
    
            try:
                # Run a test trade if true
                if test_mode:
                    order[coin['symbol']] = {
                                'symbol':symbol_only+pairing,
                                'price':price,
                                'volume':volume,
                                'time':datetime.timestamp(datetime.now()),
                                'tp': tp,
                                'sl': sl
                                }
    
                    print('PLACING TEST ORDER')
    
                # place a live order if False
                else:
                    order[coin['symbol']] = create_order(symbol_only+pairing, volume, 'BUY')
                    order[coin['symbol']]['tp'] = tp
                    order[coin['symbol']]['sl'] = sl
    
            except Exception as e:
                print(e)
    
            else:
                print(f"Order created with {volume} on {coin['symbol']}")
    
                store_order('order.json', order)
        else:
            print(f"New coin detected, but {coin['symbol']} is currently in portfolio, or {pairing} does not match")


def handle_coin(coin, order, pairing, enable_tsl, tp, ttp, tsl, sl, test_mode):
    """Handle coin."""
    coin_order = order[coin]
    # store some necessary trade info for a sell
    stored_price = float(coin_order['price'])
    coin_tp = coin_order['tp']
    # coin_sl = coin_order['sl']
    volume = coin_order['volume']
    symbol = coin.split(pairing)[0]

    # take profit price from order
    # this gets increased if enable_tsl and if it increases more than % specified in config.
    stored_price_tp = stored_price + (stored_price*coin_tp/100)

    # take profit price
    # take profit if coin increased more than tp% in config.yml, when no enable_tsl enabled
    original_tp = stored_price + (stored_price*tp /100)
    # config sp% less than stored price
    stored_price_sl = stored_price - (stored_price*sl /100)
    
    last_price = get_price(symbol, pairing)
    last_price_f = float(last_price)
    
    # update stop loss and take profit values if threshold is reached
    if enable_tsl and last_price_f > stored_price_tp:
        # increase as absolute value for TP
        new_tp = last_price_f + (last_price_f*ttp /100)
        # convert back into % difference from when the coin was bought
        new_tp = float( (new_tp - stored_price) / stored_price*100)
    
        # same deal as above, only applied to trailing SL
        new_sl = last_price_f - (last_price_f*tsl /100)
        new_sl = float((new_sl - stored_price) / stored_price*100)
    
        # new values to be added to the json file
        coin_order['tp'] = new_tp
        coin_order['sl'] = new_sl
        store_order('order.json', order)
    
        print(f'updated tp: {round(new_tp, 3)} and sl: {round(new_sl, 3)}')
    
    # close trade if tsl is reached or trail option is not enabled
    elif last_price_f < stored_price_sl or last_price_f > original_tp and not enable_tsl:
        try:
            # sell for real if test mode is set to false
            if not test_mode:
                sell = create_order(coin, coin['volume'], 'SELL')
    
    
            print(f"sold {coin} at {(last_price_f - stored_price) / float(stored_price)*100}")
    
            # remove order from json file
            order.pop(coin)
            store_order('order.json', order)

            # store sold trades data
            if os.path.isfile('sold.json'):
                sold_coins = load_order('sold.json')
            else:
                sold_coins = {}
    
            if test_mode:
                sold_coins[coin] = {
                            'symbol':coin,
                            'price':last_price,
                            'volume':volume,
                            'time':datetime.timestamp(datetime.now()),
                            'profit': last_price_f - stored_price,
                            'relative_profit': round((last_price_f - stored_price) / stored_price*100, 3)
                            }
            else:
                sold_coins[coin] = sell
    
            store_order('sold.json', sold_coins)
    
        except Exception as e:
            print(e)



def main():
    """
    Sells, adjusts TP and SL according to trailing values
    and buys new coins
    """
    # store config deets
    tp = config['TRADE_OPTIONS']['TP']
    sl = config['TRADE_OPTIONS']['SL']
    enable_tsl = config['TRADE_OPTIONS']['ENABLE_TSL']
    tsl = config['TRADE_OPTIONS']['TSL']
    ttp = config['TRADE_OPTIONS']['TTP']
    pairing = config['TRADE_OPTIONS']['PAIRING']
    qty = config['TRADE_OPTIONS']['QUANTITY']
    frequency_seconds = config['TRADE_OPTIONS']['RUN_EVERY'] * 60
    test_mode = config['TRADE_OPTIONS']['TEST']

    all_coins = get_all_coins()
    coin_seen_dict = generate_coin_seen_dict(all_coins)

    # simulate new coin
    # if test_mode:
    #     coin_seen_dict.pop('ADAUSDT')

    while True:
        started_at = datetime.utcnow()
        try:

            # check if the order file exists and load the current orders
            # basically the sell block and update TP and SL logic
            if os.path.isfile('order.json'):
                order = load_order('order.json')
                for coin in list(order):
                    handle_coin(coin, order, pairing, enable_tsl, tp, ttp, tsl, sl, test_mode)

            else:
                order = {}

            # check if new coins are listed
            new_coins = get_new_coins(coin_seen_dict)

            # the buy block and logic pass
            if len(new_coins) > 0:
                handle_new_coin(new_coins, qty, order, pairing, tp, sl, test_mode)
            else:
                pass

        except Exception as e:
            print(e)

        diff = (datetime.utcnow() - started_at).total_seconds()
        print(diff)
        if diff < frequency_seconds:
            to_sleep = frequency_seconds - diff
            print('sleeping {}s'.format(round(to_sleep, 2)))
            sleep(to_sleep)  # sleep remaining time until next loop


if __name__ == '__main__':
    print('working...')
    main()
