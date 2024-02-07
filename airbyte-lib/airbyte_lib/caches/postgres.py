# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A Postgres implementation of the cache."""

from __future__ import annotations

from overrides import overrides

from airbyte_lib._file_writers import ParquetWriter, ParquetWriterConfig
from airbyte_lib.caches.base import SQLCacheBase, SQLCacheConfigBase
from airbyte_lib.telemetry import CacheTelemetryInfo


class PostgresCacheConfig(SQLCacheConfigBase, ParquetWriterConfig):
    """Configuration for the Postgres cache.

    Also inherits config from the ParquetWriter, which is responsible for writing files to disk.
    """

    host: str
    port: int
    username: str
    password: str
    database: str

    # Already defined in base class: `schema_name`

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def get_database_name(self) -> str:
        """Return the name of the database."""
        return self.database


class PostgresCache(SQLCacheBase):
    """A Postgres implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.

    TOOD: Add optimized bulk load path for Postgres. Could use an alternate file writer
    or another import method. (Relatively low priority, since for now it works fine as-is.)
    """

    config_class = PostgresCacheConfig
    file_writer_class = ParquetWriter
    supports_merge_insert = False  # TODO: Add native implementation for merge insert

    @overrides
    def get_telemetry_info(self) -> CacheTelemetryInfo:
        return CacheTelemetryInfo("postgres")
