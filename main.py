import asyncio
from typing import List
import logging
import time
from util import Config, Util
from bot import Bot
import traceback

Config.load_global_config()

# setup logging
Util.setup_logging(name="new-coin-bot", level=Config.PROGRAM_OPTIONS["LOG_LEVEL"])

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel("INFO")
errLogger = logging.getLogger("error_log")
errLogger.propagate = False


def setup() -> List[Bot]:
    logger.info("Creating bots..")

    # Create bots based on config
    b = []
    for broker in Config.ENABLED_BROKERS:
        logger.info("Creating bot [{}]".format(broker))
        b.append(Bot(broker))
    return b


async def forever(routines: List):
    while True:
        t = time.time()
        await main(routines)
        logger.debug("Loop Finished:\t{} seconds".format(time.time() - t))
        logger.debug("Sleeping for [{}] seconds".format(Config.FREQUENCY_SECONDS))
        await asyncio.sleep(Config.FREQUENCY_SECONDS)


async def main(bots_: List):
    coroutines = [b.run_async() for b in bots_]

    # This returns the results one by one.
    for future in asyncio.as_completed(coroutines):
        await future


if __name__ == "__main__":
    logger.info("Starting..")
    loop = asyncio.get_event_loop()
    bots = setup()
    try:
        loop.create_task(forever(bots))
        loop.run_forever()
    except KeyboardInterrupt as e:
        logger.info("Exiting program..")
    except Exception as e:
        errLogger.error(traceback.format_exc())
    finally:
        for bot in bots:
            bot.save()
