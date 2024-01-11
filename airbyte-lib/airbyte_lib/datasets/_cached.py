# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from airbyte_lib.datasets._base import DatasetBase


if TYPE_CHECKING:
    from pandas import DataFrame
    from sqlalchemy import Table

    from airbyte_lib.caches import SQLCacheBase


class CachedDataset(DatasetBase):
    def __init__(self, cache: "SQLCacheBase", stream: str) -> None:
        self._cache = cache
        self._stream = stream
        self._iterator = iter(self._cache.get_records(self._stream))

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Mapping[str, Any]:
        return next(self._iterator)

    def to_pandas(self) -> "DataFrame":
        return self._cache.get_pandas_dataframe(self._stream)

    def to_sql_table(self) -> "Table":
        return self._cache.get_sql_table(self._stream)
