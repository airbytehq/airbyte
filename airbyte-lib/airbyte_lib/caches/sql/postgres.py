"""A Postgres implementation of the cache."""

from __future__ import annotations


from airbyte_lib.bases import SQLCache, SQLCacheConfigBase

from airbyte_lib.parquet import ParquetCache, ParquetCacheConfig
from overrides import overrides


class PostgresCacheConfig(SQLCacheConfigBase, ParquetCacheConfig):
    """Configuration for the Postgres cache.

    Also inherits config from the ParquetCache, which is responsible for writing files to disk.
    """

    type: str = "postgres"
    host: str
    port: int
    username: str
    password: str
    database: str

    # Already defined in base class:
    # schema: str

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?schema={self.schema}"


class PostgresSQLCache(SQLCache, ParquetCache):
    """A Postgres implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.
    """

    config_class = PostgresCacheConfig
