# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from typing import Iterable

from airbyte_protocol.models import AirbyteRecordMessage

from airbyte_lib.caches.base import SQLCacheBase, SQLCacheConfigBase
from airbyte_lib.file_writers import FileWriterBase, FileWriterConfigBase


class InMemoryCacheConfig(SQLCacheConfigBase):
    """Configuration for the in-memory cache."""

    type: str = "in_memory"


class InMemoryFileWriterConfig(FileWriterConfigBase):
    """Configuration for the in-memory cache."""

    type: str = "in_memory"


class InMemoryFileWriterEmulator(FileWriterBase):
    """The in-memory cache file writer writes to RAM files."""

    config_class = InMemoryFileWriterConfig


class InMemoryCache(SQLCacheBase):
    """The in-memory cache is accepting airbyte messages and stores them in a dictionary for streams (one list of dicts per stream)."""

    config_class = InMemoryCacheConfig
    file_writer_class = InMemoryFileWriterEmulator

    def write(self, messages: Iterable[AirbyteRecordMessage]) -> None:
        for message in messages:
            if message.stream not in self.streams:
                self.streams[message.stream] = []
            self.streams[message.stream].append(message.data)
