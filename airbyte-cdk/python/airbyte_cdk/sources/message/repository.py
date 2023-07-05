#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Callable, Iterable

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, Type

_SUPPORTED_MESSAGE_TYPES = {Type.CONTROL, Type.LOG}


class MessageRepository(ABC):
    @abstractmethod
    def emit_message(self, message: AirbyteMessage) -> None:
        raise NotImplementedError()

    @abstractmethod
    def log_message(self, level: Level, message_provider: Callable[[], AirbyteMessage])  -> None:
        """
        Computing messages can be resource consuming. This method is specialized for logging because we want to allow for lazy evaluation if
        the log level is less severe than what is configured
        """
        raise NotImplementedError()

    @abstractmethod
    def consume_queue(self) -> Iterable[AirbyteMessage]:
        raise NotImplementedError()


class NoopMessageRepository(MessageRepository):
    def emit_message(self, message: AirbyteMessage) -> None:
        pass

    def log_message(self, level: Level, message_provider: Callable[[], AirbyteMessage]) -> None:
        pass

    def consume_queue(self) -> Iterable[AirbyteMessage]:
        return []


class InMemoryMessageRepository(MessageRepository):
    _SEVERITY_BY_LOG_LEVEL = {
        Level.FATAL: 1,
        Level.ERROR: 2,
        Level.WARN: 3,
        Level.INFO: 4,
        Level.DEBUG: 5,
        Level.TRACE: 5,
    }

    def __init__(self, log_level=Level.INFO):
        self._message_queue = []
        self._log_level = log_level

    def emit_message(self, message: AirbyteMessage) -> None:
        """
        :param message: As of today, only AirbyteControlMessages are supported given that supporting other types of message will need more
          work and therefore this work has been postponed
        """
        if message.type not in _SUPPORTED_MESSAGE_TYPES:
            raise ValueError(f"As of today, only {_SUPPORTED_MESSAGE_TYPES} are supported as part of the InMemoryMessageRepository")
        self._message_queue.append(message)

    def log_message(self, level: Level, message_provider: Callable[[], AirbyteMessage]) -> None:
        if self._SEVERITY_BY_LOG_LEVEL[self._log_level] >= self._SEVERITY_BY_LOG_LEVEL[level]:
            self.emit_message(AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=level, message=message_provider())))

    def consume_queue(self) -> Iterable[AirbyteMessage]:
        while self._message_queue:
            yield self._message_queue.pop(0)
