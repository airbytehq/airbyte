# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, cast

from overrides import overrides
from sqlalchemy import all_, text

from airbyte_lib.datasets._base import DatasetBase


if TYPE_CHECKING:
    from collections.abc import Iterator

    from pandas import DataFrame
    from sqlalchemy import Selectable, Table
    from sqlalchemy.sql import ClauseElement

    from airbyte_lib.caches import SQLCacheBase


class SQLDataset(DatasetBase):
    """A dataset that is loaded incrementally from a SQL query.

    The CachedDataset class is a subclass of this class, which simply passes a SELECT over the full
    table as the query statement.
    """

    def __init__(
        self,
        cache: SQLCacheBase,
        stream_name: str,
        query_statement: Selectable,
    ) -> None:
        self._cache: SQLCacheBase = cache
        self._stream_name: str = stream_name
        self._query_statement: Selectable = query_statement

    def __iter__(self) -> Iterator[Mapping[str, Any]]:
        with self._cache.get_sql_connection() as conn:
            for row in conn.execute(self._query_statement):
                # Access to private member required because SQLAlchemy doesn't expose a public API.
                # https://pydoc.dev/sqlalchemy/latest/sqlalchemy.engine.row.RowMapping.html
                yield cast(Mapping[str, Any], row._mapping)  # noqa: SLF001

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, SQLDataset):
            return False

        if self._cache is not __value._cache:
            return False

        if self._stream_name != __value._stream_name:
            return False

        if self._query_statement != __value._query_statement:
            return False

        return True

    def to_pandas(self) -> DataFrame:
        return self._cache.get_pandas_dataframe(self._stream_name)


class CachedDataset(SQLDataset):
    """A dataset backed by a SQL table cache.

    Because this dataset includes all records from the underlying table, we also expose the
    underlying table as a SQLAlchemy Table object.
    """

    def __init__(self, cache: SQLCacheBase, stream_name: str) -> None:
        self._cache: SQLCacheBase = cache
        self._stream_name: str = stream_name
        self._query_statement: Selectable = self.to_sql_table().select()

    @overrides
    def to_pandas(self) -> DataFrame:
        return self._cache.get_pandas_dataframe(self._stream_name)

    def to_sql_table(self) -> Table:
        return self._cache.get_sql_table(self._stream_name)

    def with_filter(self, *filter_expressions: ClauseElement | str) -> SQLDataset:
        """Filter the dataset by a set of column values.

        Filters can be specified as either a string or a SQLAlchemy expression.
        """
        # Convert all strings to TextClause objects.
        filters: list[ClauseElement] = [
            text(expression) if isinstance(expression, str) else expression
            for expression in filter_expressions
        ]
        filtered_select = self._query_statement.where(all_(*filters))
        return SQLDataset(
            cache=self._cache,
            stream_name=self._stream_name,
            query_statement=filtered_select,
        )
