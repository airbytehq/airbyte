#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Iterable

from airbyte_cdk.models import AirbyteMessage, Type


class MessageRepository(ABC):
    @abstractmethod
    def emit_message(self, message: AirbyteMessage) -> None:
        raise NotImplementedError()

    @abstractmethod
    def consume_queue(self) -> Iterable[AirbyteMessage]:
        raise NotImplementedError()


class InMemoryMessageRepository(MessageRepository):
    def __init__(self):
        self._message_queue = []

    def emit_message(self, message: AirbyteMessage) -> None:
        """
        :param message: As of today, only AirbyteControlMessages are supported given that supporting other types of message will need more
          work and therefore this work has been postponed
        """
        if message.type != Type.CONTROL:
            raise ValueError("As of today, only AirbyteControlMessages are supported as part of the InMemoryMessageRepository")
        self._message_queue.append(message)

    def consume_queue(self) -> Iterable[AirbyteMessage]:
        while self._message_queue:
            yield self._message_queue.pop(0)
