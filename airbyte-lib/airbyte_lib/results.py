# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from airbyte_lib.datasets import CachedDataset


if TYPE_CHECKING:
    from collections.abc import Iterator

    from sqlalchemy.engine import Engine

    from airbyte_lib.caches import SQLCacheBase


class ReadResult(Mapping[str, CachedDataset]):
    def __init__(
        self, processed_records: int, cache: SQLCacheBase, processed_streams: list[str]
    ) -> None:
        self.processed_records = processed_records
        self._cache = cache
        self._processed_streams = processed_streams

    def __getitem__(self, stream: str) -> CachedDataset:
        if stream not in self._processed_streams:
            raise KeyError(stream)

        return CachedDataset(self._cache, stream)

    def __contains__(self, stream: object) -> bool:
        if not isinstance(stream, str):
            return False

        return stream in self._processed_streams

    def __iter__(self) -> Iterator[str]:
        return self._processed_streams.__iter__()

    def __len__(self) -> int:
        return len(self._processed_streams)

    def get_sql_engine(self) -> Engine:
        return self._cache.get_sql_engine()

    @property
    def streams(self) -> Mapping[str, CachedDataset]:
        return {
            stream_name: CachedDataset(self._cache, stream_name)
            for stream_name in self._processed_streams
        }

    @property
    def cache(self) -> SQLCacheBase:
        return self._cache
