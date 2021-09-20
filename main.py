import asyncio
from typing import List
import time
from util import Config, Util
from bot import Bot
import traceback

Config.load_global_config()

# setup logging
Util.setup_logging(name="new-coin-bot", level=Config.PROGRAM_OPTIONS["LOG_LEVEL"])


def setup() -> List[Bot]:
    Config.NOTIFICATION_SERVICE.send_info("Creating bots..")

    # Create bots based on config
    b = []
    for broker in Config.ENABLED_BROKERS:
        Config.NOTIFICATION_SERVICE.send_info("Creating bot [{}]".format(broker))
        b.append(Bot(broker))
    return b


async def forever(routines: List):
    while True:
        t = time.time()
        await main(routines)
        Config.NOTIFICATION_SERVICE.send_debug(
            "Loop finished in [{}] seconds".format(time.time() - t)
        )
        Config.NOTIFICATION_SERVICE.send_debug(
            "Sleeping for [{}] seconds".format(Config.FREQUENCY_SECONDS)
        )
        await asyncio.sleep(Config.FREQUENCY_SECONDS)


async def main(bots_: List):
    coroutines = [b.run_async() for b in bots_]

    # This returns the results one by one.
    for future in asyncio.as_completed(coroutines):
        await future


if __name__ == "__main__":
    Config.NOTIFICATION_SERVICE.send_info("Starting..")
    loop = asyncio.get_event_loop()
    bots = setup()
    try:
        loop.create_task(forever(bots))
        loop.run_forever()
    except KeyboardInterrupt as e:
        Config.NOTIFICATION_SERVICE.send_info("Exiting program..")
    except Exception as e:
        Config.NOTIFICATION_SERVICE.send_error(traceback.format_exc())
    finally:
        for bot in bots:
            bot.save()
