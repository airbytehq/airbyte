# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, cast

from overrides import overrides
from sqlalchemy import and_, func, select, text

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
        self._length: int | None = None
        self._cache: SQLCacheBase = cache
        self._stream_name: str = stream_name
        self._query_statement: Selectable = query_statement
        super().__init__()

    @property
    def stream_name(self) -> str:
        return self._stream_name

    def __iter__(self) -> Iterator[Mapping[str, Any]]:
        with self._cache.get_sql_connection() as conn:
            for row in conn.execute(self._query_statement):
                # Access to private member required because SQLAlchemy doesn't expose a public API.
                # https://pydoc.dev/sqlalchemy/latest/sqlalchemy.engine.row.RowMapping.html
                yield cast(Mapping[str, Any], row._mapping)  # noqa: SLF001

    def __len__(self) -> int:
        """Return the number of records in the dataset.

        This method caches the length of the dataset after the first call.
        """
        if self._length is None:
            count_query = select([func.count()]).select_from(self._query_statement.alias())
            with self._cache.get_sql_connection() as conn:
                self._length = conn.execute(count_query).scalar()

        return self._length

    def to_pandas(self) -> DataFrame:
        return self._cache.get_pandas_dataframe(self._stream_name)

    def with_filter(self, *filter_expressions: ClauseElement | str) -> SQLDataset:
        """Filter the dataset by a set of column values.

        Filters can be specified as either a string or a SQLAlchemy expression.

        Filters are lazily applied to the dataset, so they can be chained together. For example:

                dataset.with_filter("id > 5").with_filter("id < 10")

        is equivalent to:

                dataset.with_filter("id > 5", "id < 10")
        """
        # Convert all strings to TextClause objects.
        filters: list[ClauseElement] = [
            text(expression) if isinstance(expression, str) else expression
            for expression in filter_expressions
        ]
        filtered_select = self._query_statement.where(and_(*filters))
        return SQLDataset(
            cache=self._cache,
            stream_name=self._stream_name,
            query_statement=filtered_select,
        )


class CachedDataset(SQLDataset):
    """A dataset backed by a SQL table cache.

    Because this dataset includes all records from the underlying table, we also expose the
    underlying table as a SQLAlchemy Table object.
    """

    def __init__(self, cache: SQLCacheBase, stream_name: str) -> None:
        self._sql_table: Table = cache.get_sql_table(stream_name)
        super().__init__(
            cache=cache,
            stream_name=stream_name,
            query_statement=self._sql_table.select(),
        )

    @overrides
    def to_pandas(self) -> DataFrame:
        return self._cache.get_pandas_dataframe(self._stream_name)

    def to_sql_table(self) -> Table:
        return self._sql_table

    def __eq__(self, value: object) -> bool:
        """Return True if the value is a CachedDataset with the same cache and stream name.

        In the case of CachedDataset objects, we can simply compare the cache and stream name.

        Note that this equality check is only supported on CachedDataset objects and not for
        the base SQLDataset implementation. This is because of the complexity and computational
        cost of comparing two arbitrary SQL queries that could be bound to different variables,
        as well as the chance that two queries can be syntactically equivalent without being
        text-wise equivalent.
        """
        if not isinstance(value, SQLDataset):
            return False

        if self._cache is not value._cache:
            return False

        if self._stream_name != value._stream_name:
            return False

        return True
