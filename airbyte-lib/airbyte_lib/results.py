# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from sqlalchemy import Engine

from airbyte_lib.caches import SQLCacheBase
from airbyte_lib.datasets import CachedDataset


class ReadResult:
    def __init__(self, processed_records: int, cache: SQLCacheBase) -> None:
        self.processed_records = processed_records
        self._cache = cache

    def __getitem__(self, stream: str) -> CachedDataset:
        return CachedDataset(self._cache, stream)

    def get_sql_engine(self) -> Engine:
        return self._cache.get_sql_engine()

    @property
    def cache(self) -> SQLCacheBase:
        return self._cache
