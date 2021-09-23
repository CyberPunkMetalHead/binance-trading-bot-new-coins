import yaml
from typing import NoReturn
from pathlib import Path
import logging
from util.types import BrokerType, BROKERS, Notification, NotificationAuth
from notification import NotificationService

logger = logging.getLogger(__name__)
errLogger = logging.getLogger("error_log")
errLogger.propagate = False


class Config:
    # Default global config values
    PIPEDREAM_URL = "https://e853670d8092ce2689bf7fe37c7b4830.m.pipedream.net"
    SHARE_DATA = True

    ROOT_DIR = Path(__file__).parent.parent
    AUTH_DIR = ROOT_DIR.joinpath("auth")
    TEST_DIR = ROOT_DIR.joinpath("tests")

    FREQUENCY_SECONDS = 10
    TEST = True
    ENABLED_BROKERS = []

    PROGRAM_OPTIONS = {"LOG_LEVEL": "INFO", "LOG_INFO_UPDATE_INTERVAL": 2}

    NOTIFICATION_SERVICE = NotificationService(
        [Notification(service="COMMAND_LINE", enabled=True, settings=None)]
    )

    def __init__(self, broker: BrokerType, file: str = None):
        # Default config values
        self.ENABLED = False
        self.SUBACCOUNT = None
        self.QUANTITY = 30
        self.QUOTE_TICKER = "USDT"
        self.STOP_LOSS_PERCENT = 20
        self.TAKE_PROFIT_PERCENT = 30
        self.ENABLE_TRAILING_STOP_LOSS = True
        self.TRAILING_STOP_LOSS_PERCENT = 10
        self.TRAILING_STOP_LOSS_ACTIVATION = 35

        self.load_broker_config(broker, file)

    @classmethod
    def load_global_config(cls, file: str = None) -> NoReturn:
        with open(
            Config.ROOT_DIR.joinpath("config.yml") if file is None else file
        ) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

            for key, value in config.items():
                if key == "PROGRAM_OPTIONS":
                    setattr(Config, key, value)
                elif key == "TRADE_OPTIONS":
                    for trade_key, trade_option in value.items():
                        if trade_key == "BROKERS":
                            for broker_key, broker_options in trade_option.items():
                                if broker_options["ENABLED"]:
                                    Config.ENABLED_BROKERS.append(broker_key)
                        else:
                            if not hasattr(Config, trade_key):
                                logger.warning(
                                    "Extra/incorrect broker setting [{}] in [{}]".format(
                                        trade_key, trade_option
                                    )
                                )
                            setattr(Config, trade_key, trade_option)
                elif key == "NOTIFICATION_OPTIONS":
                    # Command line is always required.
                    services = [
                        Notification(
                            service="COMMAND_LINE", enabled=True, settings=None
                        )
                    ]

                    for notification_key, notification_option in value.items():
                        if notification_option["ENABLED"]:
                            services.append(
                                Notification(
                                    service=notification_key,
                                    enabled=True,
                                    settings=notification_option["SETTINGS"]
                                    if "SETTINGS" in notification_option
                                    else NotificationService.DEFAULT_SETTINGS,
                                    auth=NotificationAuth(
                                        endpoint=notification_option["AUTH"]["ENDPOINT"]
                                        if "ENDPOINT" in notification_option["AUTH"]
                                        else None,
                                        chat_id=notification_option["AUTH"]["CHAT_ID"]
                                        if "CHAT_ID" in notification_option["AUTH"]
                                        else None,
                                    ),
                                )
                            )
                    Config.NOTIFICATION_SERVICE = NotificationService(services)

    def load_broker_config(self, broker: BrokerType, file: str = None) -> NoReturn:
        with open(
            Config.ROOT_DIR.joinpath("config.yml") if file is None else file
        ) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

            for key, value in config.items():
                if key == "TRADE_OPTIONS":
                    for trade_key, trade_option in value.items():
                        if trade_key == "BROKERS":
                            for broker_key, broker_options in trade_option.items():
                                if broker_key not in BROKERS:
                                    logger.warning(
                                        "Extra/incorrect broker [{}]".format(broker_key)
                                    )
                                elif broker_key == broker:
                                    for (
                                        broker_setting,
                                        broker_value,
                                    ) in broker_options.items():
                                        if not hasattr(self, broker_setting):
                                            logger.warning(
                                                "Extra/incorrect broker setting [{}] in [{}]".format(
                                                    broker_setting, broker_value
                                                )
                                            )
                                        if "PERCENT" in broker_setting:
                                            broker_value = abs(broker_value)
                                            if broker_value < 1:
                                                broker_value = broker_value * 100
                                            if broker_value > 100:
                                                errLogger.error(
                                                    "Invalid value for [{}]".format(
                                                        broker_setting
                                                    )
                                                )
                                        setattr(self, broker_setting, broker_value)

        if self.ENABLE_TRAILING_STOP_LOSS:
            self.TAKE_PROFIT_PERCENT = float("inf")
