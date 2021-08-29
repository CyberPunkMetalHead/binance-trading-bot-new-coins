import asyncio
import socket
from configparser import ConfigParser

from binance import AsyncClient, BinanceSocketManager
from telegram import Bot, Chat

config = ConfigParser()
config.add_section("bot")
config.read("config.ini")


def get_client_configs():
    tld = config["binance"].get("tld")
    return dict(
        api_key=config["binance"]["api"],
        api_secret=config["binance"]["secret"],
        tld="com" if not tld else tld,
    )


def get_new_coins(msg, coins):
    return [item for item in msg if item["s"] not in coins]


async def main():
    client = await AsyncClient(**get_client_configs()).create()
    bm = BinanceSocketManager(client)

    tbot = Bot(config["telegram"]["token"])
    chat_id = int(config["telegram"]["chat_id"])
    chat = Chat(chat_id, "private", bot=tbot)
    chat.send_message(f"starting binance watcher in {socket.gethostname()}")

    sock = bm.ticker_socket()

    tickers = await client.get_all_tickers()
    coins = set([item["symbol"] for item in tickers])

    # then start receiving messages
    async with sock:
        while True:
            msg = await sock.recv()

            new_coins = get_new_coins(msg, coins)
            # sample new coin, add one to new_coins list
            # coin = msg[0]
            # new_coins.append(coin)

            if len(new_coins) > 0:
                keys = [item["s"] for item in new_coins]
                chat.send_message(f"new coins!!: {keys}")
                break
            else:
                pass
                # print('no new coins...')

    await client.close_connection()


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
