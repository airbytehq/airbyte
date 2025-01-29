# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from airbyte_protocol.models import AirbyteMessage  # type: ignore


class BaseBackend(ABC):
    """
    Interface to be shared between the file backend and the database backend(s)
    """

    @abstractmethod
    def write(self, airbyte_messages: Iterable[AirbyteMessage]) -> None: ...
