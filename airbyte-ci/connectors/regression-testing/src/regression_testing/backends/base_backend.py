from abc import ABC, abstractmethod
from typing import Any, Generator

from airbyte_protocol.models import AirbyteMessage


class BaseBackend(ABC):  # TODO
    """
    Interface to be shared between the file backend and the database backend(s)
    """

    @abstractmethod
    async def write(self, raw_output: Generator[AirbyteMessage, Any, None]) -> None:
        ...

    @abstractmethod
    async def read(self) -> None:
        ...

    @abstractmethod
    async def compare(self) -> None:
        ...
