# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from collections.abc import Iterable
from typing import Any

from pandas import DataFrame
from sqlalchemy import Table

from airbyte_lib.caches import SQLCacheBase


class Dataset:
    def __init__(self, cache: SQLCacheBase, stream: str) -> None:
        self._cache = cache
        self._stream = stream

    def __iter__(self) -> Iterable[dict[str, Any]]:
        return self._cache.get_records(self._stream)

    def to_pandas(self) -> DataFrame:
        return self._cache.get_pandas_dataframe(self._stream)

    def to_sql_table(self) -> Table:
        return self._cache.get_sql_table(self._stream)
