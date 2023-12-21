"""A DuckDB implementation of the cache."""

from __future__ import annotations

from overrides import overrides

from airbyte_lib.caches.base import SQLCacheBase, SQLCacheConfigBase
from airbyte_lib.file_writers import ParquetWriter, ParquetWriterConfig


class DuckDBCacheConfig(SQLCacheConfigBase, ParquetWriterConfig):
    """Configuration for the DuckDB cache.

    Also inherits config from the ParquetWriter, which is responsible for writing files to disk.
    """

    type: str = "duckdb"
    db_path: str

    # Already defined in base class:
    # schema_name: str

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        return f"duckdb://{self.db_path}?schema={self.schema_name}"


class DuckDBSQLCache(SQLCacheBase):
    """A DuckDB implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.
    """

    config_class = DuckDBCacheConfig
    file_writer_class = ParquetWriter
