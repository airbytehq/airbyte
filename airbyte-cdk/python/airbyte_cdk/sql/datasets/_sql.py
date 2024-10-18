# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""SQL datasets class."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, Literal, cast

from overrides import overrides
from sqlalchemy import and_, func, select, text

from airbyte_cdk.models import ConfiguredAirbyteStream

from airbyte_cdk.sql.constants import DEFAULT_ARROW_MAX_CHUNK_SIZE
from airbyte_cdk.sql.datasets._base import DatasetBase


if TYPE_CHECKING:
    from collections.abc import Iterator

    from pandas import DataFrame
    from pyarrow.dataset import Dataset
    from sqlalchemy import Table
    from sqlalchemy.sql import ClauseElement
    from sqlalchemy.sql.expression import Select

    from airbyte_cdk.models import ConfiguredAirbyteStream

    from airbyte_cdk.sql.caches.base import CacheBase


class SQLDataset(DatasetBase):
    """A dataset that is loaded incrementally from a SQL query.

    The CachedDataset class is a subclass of this class, which simply passes a SELECT over the full
    table as the query statement.
    """

    def __init__(
        self,
        cache: CacheBase,
        stream_name: str,
        query_statement: Select,
        stream_configuration: ConfiguredAirbyteStream | None | Literal[False] = None,
    ) -> None:
        """Initialize the dataset with a cache, stream name, and query statement.

        This class is not intended to be created directly. Instead, you can retrieve
        datasets from caches or Cloud connection objects, etc.

        The query statement should be a SQLAlchemy Selectable object that can be executed to
        retrieve records from the dataset.

        If stream_configuration is not provided, we attempt to retrieve the stream configuration
        from the cache processor. This is useful when constructing a dataset from a CachedDataset
        object, which already has the stream configuration.

        If stream_configuration is set to False, we skip the stream configuration retrieval.
        """
        self._length: int | None = None
        self._cache: CacheBase = cache
        self._stream_name: str = stream_name
        self._query_statement: Select = query_statement
        if stream_configuration is None:
            try:
                stream_configuration = cache.processor.catalog_provider.get_configured_stream_info(
                    stream_name=stream_name
                )
            except Exception as ex:
                warnings.warn(
                    f"Failed to get stream configuration for {stream_name}: {ex}",
                    stacklevel=2,
                )

        # Coalesce False to None
        stream_configuration = stream_configuration or None

        super().__init__(stream_metadata=stream_configuration)

    @property
    def stream_name(self) -> str:
        return self._stream_name

    def __iter__(self) -> Iterator[dict[str, Any]]:
        with self._cache.processor.get_sql_connection() as conn:
            for row in conn.execute(self._query_statement):
                # Access to private member required because SQLAlchemy doesn't expose a public API.
                # https://pydoc.dev/sqlalchemy/latest/sqlalchemy.engine.row.RowMapping.html
                yield cast(dict[str, Any], row._mapping)  # noqa: SLF001

    def __len__(self) -> int:
        """Return the number of records in the dataset.

        This method caches the length of the dataset after the first call.
        """
        if self._length is None:
            count_query = select(func.count()).select_from(self._query_statement.subquery())
            with self._cache.processor.get_sql_connection() as conn:
                self._length = conn.execute(count_query).scalar()

        return cast(int, self._length)

    def to_pandas(self) -> DataFrame:
        return self._cache.get_pandas_dataframe(self._stream_name)

    def to_arrow(
        self,
        *,
        max_chunk_size: int = DEFAULT_ARROW_MAX_CHUNK_SIZE,
    ) -> Dataset:
        return self._cache.get_arrow_dataset(self._stream_name, max_chunk_size=max_chunk_size)

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
        filtered_select = self._query_statement.where(and_(*filters)) # type: ignore
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

    def __init__(
        self,
        cache: CacheBase,
        stream_name: str,
        stream_configuration: ConfiguredAirbyteStream | None | Literal[False] = None,
    ) -> None:
        """We construct the query statement by selecting all columns from the table.

        This prevents the need to scan the table schema to construct the query statement.

        If stream_configuration is None, we attempt to retrieve the stream configuration from the
        cache processor. This is useful when constructing a dataset from a CachedDataset object,
        which already has the stream configuration.

        If stream_configuration is set to False, we skip the stream configuration retrieval.
        """
        table_name = cache.processor.get_sql_table_name(stream_name)
        schema_name = cache.schema_name
        query = select("*").select_from(text(f"{schema_name}.{table_name}"))
        super().__init__(
            cache=cache,
            stream_name=stream_name,
            query_statement=query,
            stream_configuration=stream_configuration,
        )

    @overrides
    def to_pandas(self) -> DataFrame:
        """Return the underlying dataset data as a pandas DataFrame."""
        return self._cache.get_pandas_dataframe(self._stream_name)

    @overrides
    def to_arrow(
        self,
        *,
        max_chunk_size: int = DEFAULT_ARROW_MAX_CHUNK_SIZE,
    ) -> Dataset:
        """Return an Arrow Dataset containing the data from the specified stream.

        Args:
            stream_name (str): Name of the stream to retrieve data from.
            max_chunk_size (int): max number of records to include in each batch of pyarrow dataset.

        Returns:
            pa.dataset.Dataset: Arrow Dataset containing the stream's data.
        """
        return self._cache.get_arrow_dataset(
            stream_name=self._stream_name,
            max_chunk_size=max_chunk_size,
        )

    def to_sql_table(self) -> Table:
        """Return the underlying SQL table as a SQLAlchemy Table object."""
        return self._cache.processor.get_sql_table(self.stream_name)

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

        return not self._stream_name != value._stream_name

    def __hash__(self) -> int:
        return hash(self._stream_name)
