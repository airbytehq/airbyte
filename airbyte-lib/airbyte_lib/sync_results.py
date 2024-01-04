# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Iterable

from airbyte_lib.caches import SQLCacheBase
from airbyte_lib.datasets import Dataset
from pandas import DataFrame
from sqlalchemy import Table


class SyncResult:
    def __init__(self, processed_records: int, cache: SQLCacheBase) -> None:
        self.processed_records = processed_records
        self._cache = cache

    def __getitem__(self, stream: str) -> Dataset:
        return Dataset(self._cache, stream)

    def get_sql_engine(self) -> Any:
        return self._cache.get_sql_engine()
