from typing import List, NoReturn
from abc import ABC
from util.types import *


class NotificationAbstract(ABC):
    def _send(self, message: str, *args, **kwargs):
        raise NotImplementedError

    def send_message(self, message: str, *args, **kwargs):
        raise NotImplementedError

    def send_error(self, message: str, *args, **kwargs):
        raise NotImplementedError

    def send_verbose(self, message: str, *args, **kwargs):
        raise NotImplementedError

    def send_warning(self, message: str, *args, **kwargs):
        raise NotImplementedError

    def send_info(self, message: str, *args, **kwargs):
        raise NotImplementedError

    def send_debug(self, message: str, *args, **kwargs):
        raise NotImplementedError

    def send_entry(self, order: Order, *args, **kwargs):
        raise NotImplementedError

    def send_close(self, order: Order, *args, **kwargs):
        raise NotImplementedError


class NotificationService(NotificationAbstract):
    DEFAULT_SETTINGS = {
        "SEND_MESSAGE": True,
        "SEND_ERROR": True,
        "SEND_VERBOSE": False,
        "SEND_WARNING": False,
        "SEND_INFO": False,
        "SEND_DEBUG": False,
        "SEND_ENTRY": True,
        "SEND_CLOSE": True,
    }

    def __init__(self, notifications: List[Notification]) -> NoReturn:
        self.services: List[NotificationAbstract] = []

        for notification in notifications:
            if notification.enabled:
                self.services.append(NotificationService.factory(notification))

    @staticmethod
    def override_settings(settings: NotificationSettings) -> NotificationSettings:
        return NotificationSettings(
            send_message=NotificationService.DEFAULT_SETTINGS["SEND_MESSAGE"]
            or settings.send_message,
            send_error=NotificationService.DEFAULT_SETTINGS["SEND_ERROR"]
            or settings.send_error,
            send_verbose=NotificationService.DEFAULT_SETTINGS["SEND_VERBOSE"]
            or settings.send_verbose,
            send_warning=NotificationService.DEFAULT_SETTINGS["SEND_WARNING"]
            or settings.send_warning,
            send_info=NotificationService.DEFAULT_SETTINGS["SEND_INFO"]
            or settings.send_info,
            send_debug=NotificationService.DEFAULT_SETTINGS["SEND_DEBUG"]
            or settings.send_debug,
            send_entry=NotificationService.DEFAULT_SETTINGS["SEND_ENTRY"]
            or settings.send_entry,
            send_close=NotificationService.DEFAULT_SETTINGS["SEND_CLOSE"]
            or settings.send_close,
        )

    @staticmethod
    def factory(notificationModel: Notification) -> NotificationAbstract:
        from notification import (
            CommandlineNotification,
            DiscordNotification,
            TelegramNotification,
        )

        if notificationModel.service == "COMMAND_LINE":
            return CommandlineNotification()
        elif notificationModel.service == "DISCORD":
            return DiscordNotification(
                NotificationService.override_settings(notificationModel.settings),
                notificationModel.auth,
            )
        elif notificationModel.service == "TELEGRAM":
            return TelegramNotification(
                notificationModel.settings, notificationModel.auth
            )
        #     TODO
        elif notificationModel.service == "EMAIL":
            pass

    def _send(self, message: str, *args, **kwargs) -> NoReturn:
        pass

    def send_message(self, message: str, *args, **kwargs) -> NoReturn:
        [_.send_message(message, *args, **kwargs) for _ in self.services]

    def send_error(self, message: str, *args, **kwargs) -> NoReturn:
        [_.send_error(message, *args, **kwargs) for _ in self.services]

    def send_verbose(self, message: str, *args, **kwargs) -> NoReturn:
        [_.send_verbose(message, *args, **kwargs) for _ in self.services]

    def send_warning(self, message: str, *args, **kwargs) -> NoReturn:
        [_.send_warning(message, *args, **kwargs) for _ in self.services]

    def send_info(self, message: str, *args, **kwargs) -> NoReturn:
        [_.send_info(message, *args, **kwargs) for _ in self.services]

    def send_debug(self, message: str, *args, **kwargs) -> NoReturn:
        [_.send_debug(message, *args, **kwargs) for _ in self.services]

    def send_entry(self, order: Order, *args, **kwargs) -> NoReturn:
        [_.send_entry(order, *args, **kwargs) for _ in self.services]

    def send_close(self, order: Order, *args, **kwargs) -> NoReturn:
        [_.send_close(order, *args, **kwargs) for _ in self.services]
