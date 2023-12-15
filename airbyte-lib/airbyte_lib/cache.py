# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List

from airbyte_protocol.models import AirbyteRecordMessage


class Cache(ABC):
    @abstractmethod
    def write(self, messages: Iterable[AirbyteRecordMessage]):
        pass


class InMemoryCache(Cache):
    """The in-memory cache is accepting airbyte messages and stores them in a dictionary for streams (one list of dicts per stream)."""

    def __init__(self):
        self.streams: Dict[str, List[Dict[str, Any]]] = {}

    def write(self, messages: Iterable[AirbyteRecordMessage]):
        for message in messages:
            if message.stream not in self.streams:
                self.streams[message.stream] = []
            self.streams[message.stream].append(message.data)
