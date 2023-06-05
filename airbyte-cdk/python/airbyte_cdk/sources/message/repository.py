from abc import ABC, abstractmethod
from typing import Callable, Iterable

from airbyte_cdk.models import AirbyteMessage


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
        self._message_queue.append(message)

    def consume_queue(self) -> Iterable[AirbyteMessage]:
        while self._message_queue:
            yield self._message_queue.pop()
