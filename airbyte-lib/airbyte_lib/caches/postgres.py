"""A Postgres implementation of the cache."""

from __future__ import annotations

from overrides import overrides

from airbyte_lib.caches.base import SQLCacheBase, SQLCacheConfigBase
from airbyte_lib.file_writers import ParquetWriter, ParquetWriterConfig


class PostgresCacheConfig(SQLCacheConfigBase, ParquetWriterConfig):
    """Configuration for the Postgres cache.

    Also inherits config from the ParquetWriter, which is responsible for writing files to disk.
    """

    type: str = "postgres"
    host: str
    port: int
    username: str
    password: str
    database: str

    # Already defined in base class:
    # schema_name: str

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        return f"postgresql+psycopg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def get_database_name(self) -> str:
        """Return the name of the database."""
        return self.database

class PostgresCache(SQLCacheBase):
    """A Postgres implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.
    """

    config_class = PostgresCacheConfig
    file_writer_class = ParquetWriter
