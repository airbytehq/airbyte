# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from collections.abc import Iterator
from typing import Any

from airbyte_lib.caches import SQLCacheBase
from airbyte_lib.datasets import DatasetBase
from pandas import DataFrame
from sqlalchemy import Table


class CachedDataset(DatasetBase):
    def __init__(self, cache: SQLCacheBase, stream: str) -> None:
        self._cache = cache
        self._stream = stream

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return self._cache.get_records(self._stream)

    def to_pandas(self) -> DataFrame:
        return self._cache.get_pandas_dataframe(self._stream)

    def to_sql_table(self) -> Table:
        return self._cache.get_sql_table(self._stream)
