# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any

from airbyte_lib.cache import Cache


class Dataset:
    def __init__(self, cache: Cache, stream: str) -> None:
        self._cache = cache
        self._stream = stream

    def __iter__(self):
        return self._cache.get_iterable(self._stream)

    def to_pandas(self):
        return self._cache.get_pandas(self._stream)

    def to_sql_table(self):
        return self._cache.get_sql_table(self._stream)


class SyncResult:
    def __init__(self, processed_records: int, cache: Cache) -> None:
        self.processed_records = processed_records
        self._cache = cache

    def __getitem__(self, stream: str) -> Dataset:
        return Dataset(self._cache, stream)

    def get_sql_engine(self) -> Any:
        return self._cache.get_sql_engine()
