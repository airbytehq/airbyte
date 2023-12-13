"""A DuckDB implementation of the cache."""

from __future__ import annotations


from airbyte_lib.bases import SQLCache, SQLCacheConfigBase

from airbyte_lib.parquet import ParquetCache, ParquetCacheConfig
from overrides import overrides


class DuckDBCacheConfig(SQLCacheConfigBase, ParquetCacheConfig):
    """Configuration for the DuckDB cache.

    Also inherits config from the ParquetCache, which is responsible for writing files to disk.
    """

    type: str = "duckdb"
    db_path: str

    # Already defined in base class:
    # schema: str

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        return f"duckdb://{self.db_path}?schema={self.schema}"


class DuckDBSQLCache(SQLCache, ParquetCache):
    """A DuckDB implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.
    """

    config_class = DuckDBCacheConfig
