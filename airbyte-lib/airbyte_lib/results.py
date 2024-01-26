# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from typing import TYPE_CHECKING

from airbyte_lib.datasets import CachedDataset


if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from sqlalchemy.engine import Engine

    from airbyte_lib.caches import SQLCacheBase


class ReadResult:
    def __init__(self, processed_records: int, cache: SQLCacheBase) -> None:
        self.processed_records = processed_records
        self._cache = cache

    def __getitem__(self, stream: str) -> CachedDataset:
        if stream not in self._cache:
            raise KeyError(stream)

        return CachedDataset(self._cache, stream)

    def __contains__(self, stream: str) -> bool:
        return stream in self._cache

    def __iter__(self) -> Iterator[str]:
        return self._cache.__iter__()

    def get_sql_engine(self) -> Engine:
        return self._cache.get_sql_engine()

    @property
    def streams(self) -> Mapping[str, CachedDataset]:
        return self._cache.streams

    @property
    def cache(self) -> SQLCacheBase:
        return self._cache
