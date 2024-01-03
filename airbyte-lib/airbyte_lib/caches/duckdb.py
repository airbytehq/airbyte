# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A DuckDB implementation of the cache."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pyarrow as pa
from airbyte_lib.caches.base import SQLCacheBase, SQLCacheConfigBase
from airbyte_lib.file_writers import ParquetWriter, ParquetWriterConfig
from overrides import overrides


class DuckDBCacheConfig(SQLCacheConfigBase, ParquetWriterConfig):
    """Configuration for the DuckDB cache.

    Also inherits config from the ParquetWriter, which is responsible for writing files to disk.
    """

    type: str = "duckdb"
    db_path: str
    schema_name: str = "main"

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        # return f"duckdb:///{self.db_path}?schema={self.schema_name}"
        return f"duckdb:///{self.db_path}"

    def get_database_name(self) -> str:
        """Return the name of the database."""
        if self.db_path == ":memory:":
            return "memory"

        # Return the file name without the extension
        return self.db_path.split("/")[-1].split(".")[0]


class DuckDBCacheBase(SQLCacheBase):
    """A DuckDB implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.
    """

    config_class = DuckDBCacheConfig

    @overrides
    def _setup(self) -> None:
        """Create the database parent folder if it doesn't yet exist."""
        config = cast(DuckDBCacheConfig, self.config)

        if config.db_path == ":memory:":
            return

        Path(config.db_path).parent.mkdir(parents=True, exist_ok=True)


class DuckDBCache(DuckDBCacheBase):
    """A DuckDB implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.
    """

    file_writer_class = ParquetWriter
