# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""A Null (no-op) implementation of the cache.

This implementation does nothing and is useful in benchmarking the maximum
read performance of a source connection, with no time spent and no back-pressure
from writing the data to disk or to the SQL database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from overrides import overrides

from airbyte_lib._file_writers.null import NullWriter
from airbyte_lib.caches.base import SQLCacheBase, SQLCacheConfigBase
from airbyte_lib.telemetry import CacheTelemetryInfo


if TYPE_CHECKING:
    from pathlib import Path

    from pandas.core.api import DataFrame
    from sqlalchemy.schema import Table


class NullCacheConfig(SQLCacheConfigBase):
    """Configuration for the null cache."""

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return a SQLite in-memory connection.

        This should fail if the user tries to use the cache for anything.
        """
        return "sqlite:///:memory:"

    def get_database_name(self) -> str:
        return "dummy"


class NullCache(SQLCacheBase):
    """A DuckDB implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.
    """

    file_writer_class = NullWriter
    config_class = NullCacheConfig
    supports_merge_insert = True

    @overrides
    def get_telemetry_info(self) -> CacheTelemetryInfo:
        return CacheTelemetryInfo("null")

    @overrides
    def _execute_sql(self, sql: str) -> None:
        """Execute SQL."""
        _ = sql
        # Do nothing

    @overrides
    def _ensure_schema_exists(self) -> None:
        pass

    @overrides
    def _ensure_final_table_exists(
        self, stream_name: str, *, create_if_missing: bool = True
    ) -> str:
        _ = stream_name, create_if_missing
        pass

    @overrides
    def _ensure_compatible_table_schema(
        self, stream_name: str, table_name: str, *, raise_on_error: bool = False
    ) -> bool:
        _ = stream_name, table_name, raise_on_error
        pass

    @overrides
    def _write_files_to_new_table(self, files: list[Path], stream_name: str, batch_id: str) -> str:
        pass

    @overrides
    def _drop_temp_table(self, table_name: str, *, if_exists: bool = True) -> None:
        pass

    @overrides
    def _swap_temp_table_with_final_table(
        self, stream_name: str, temp_table_name: str, final_table_name: str
    ) -> None:
        pass

    @overrides
    def get_sql_table(self, stream_name: str) -> Table:  # type: ignore # noqa: PGH003 # Ignore '@final' and too-general ignore
        raise NotImplementedError("NullCache does not support get_sql_table()")

    @overrides
    def get_pandas_dataframe(self, stream_name: str) -> DataFrame:
        raise NotImplementedError("NullCache does not support get_pandas_dataframe()")
