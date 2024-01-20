#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from abc import ABC, abstractmethod
from collections import deque
from typing import Callable, Deque, Iterable, List, Optional

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, Type
from airbyte_cdk.sources.utils.types import JsonType
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets

_LOGGER = logging.getLogger("MessageRepository")
_SUPPORTED_MESSAGE_TYPES = {Type.CONTROL, Type.LOG}
LogMessage = dict[str, JsonType]

_SEVERITY_BY_LOG_LEVEL = {
    Level.FATAL: 1,
    Level.ERROR: 2,
    Level.WARN: 3,
    Level.INFO: 4,
    Level.DEBUG: 5,
    Level.TRACE: 5,
}


def _is_severe_enough(threshold: Level, level: Level) -> bool:
    if threshold not in _SEVERITY_BY_LOG_LEVEL:
        _LOGGER.warning(f"Log level {threshold} for threshold is not supported. This is probably a CDK bug. Please contact Airbyte.")
        return True

    if level not in _SEVERITY_BY_LOG_LEVEL:
        _LOGGER.warning(
            f"Log level {level} is not supported. This is probably a source bug. Please contact the owner of the source or Airbyte."
        )
        return True

    return _SEVERITY_BY_LOG_LEVEL[threshold] >= _SEVERITY_BY_LOG_LEVEL[level]


class MessageRepository(ABC):
    @abstractmethod
    def emit_message(self, message: AirbyteMessage) -> None:
        raise NotImplementedError()

    @abstractmethod
    def log_message(self, level: Level, message_provider: Callable[[], LogMessage]) -> None:
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

    def log_message(self, level: Level, message_provider: Callable[[], LogMessage]) -> None:
        pass

    def consume_queue(self) -> Iterable[AirbyteMessage]:
        return []


class InMemoryMessageRepository(MessageRepository):
    def __init__(self, log_level: Level = Level.INFO) -> None:
        self._message_queue: Deque[AirbyteMessage] = deque()
        self._log_level = log_level

    def emit_message(self, message: AirbyteMessage) -> None:
        self._message_queue.append(message)

    def log_message(self, level: Level, message_provider: Callable[[], LogMessage]) -> None:
        if _is_severe_enough(self._log_level, level):
            self.emit_message(
                AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=level, message=filter_secrets(json.dumps(message_provider()))))
            )

    def consume_queue(self) -> Iterable[AirbyteMessage]:
        while self._message_queue:
            yield self._message_queue.popleft()


class LogAppenderMessageRepositoryDecorator(MessageRepository):
    def __init__(self, dict_to_append: LogMessage, decorated: MessageRepository, log_level: Level = Level.INFO):
        self._dict_to_append = dict_to_append
        self._decorated = decorated
        self._log_level = log_level

    def emit_message(self, message: AirbyteMessage) -> None:
        self._decorated.emit_message(message)

    def log_message(self, level: Level, message_provider: Callable[[], LogMessage]) -> None:
        if _is_severe_enough(self._log_level, level):
            message = message_provider()
            self._append_second_to_first(message, self._dict_to_append)
            self._decorated.log_message(level, lambda: message)

    def consume_queue(self) -> Iterable[AirbyteMessage]:
        return self._decorated.consume_queue()

    def _append_second_to_first(self, first: LogMessage, second: LogMessage, path: Optional[List[str]] = None) -> LogMessage:
        if path is None:
            path = []

        for key in second:
            if key in first:
                if isinstance(first[key], dict) and isinstance(second[key], dict):
                    self._append_second_to_first(first[key], second[key], path + [str(key)])  # type: ignore # type is verified above
                else:
                    if first[key] != second[key]:
                        _LOGGER.warning("Conflict at %s" % ".".join(path + [str(key)]))
                    first[key] = second[key]
            else:
                first[key] = second[key]
        return first
