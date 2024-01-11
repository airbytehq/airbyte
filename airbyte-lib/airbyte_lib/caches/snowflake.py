# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A Snowflake implementation of the cache.

TODO: FIXME: Snowflake Cache doesn't work yet. It's a work in progress.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from overrides import overrides

from airbyte_lib._file_writers import ParquetWriter, ParquetWriterConfig
from airbyte_lib.caches.base import SQLCacheBase, SQLCacheConfigBase


if TYPE_CHECKING:
    from pathlib import Path


class SnowflakeCacheConfig(SQLCacheConfigBase, ParquetWriterConfig):
    """Configuration for the Snowflake cache.

    Also inherits config from the ParquetWriter, which is responsible for writing files to disk.
    """

    account: str
    username: str
    password: str
    warehouse: str
    database: str

    # Already defined in base class:
    # schema_name: str

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        return (
            f"snowflake://{self.username}:{self.password}@{self.account}/"
            f"?warehouse={self.warehouse}&database={self.database}&schema={self.schema_name}"
        )

    def get_database_name(self) -> str:
        """Return the name of the database."""
        return self.database


class SnowflakeSQLCache(SQLCacheBase):
    """A Snowflake implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    """

    config_class = SnowflakeCacheConfig
    file_writer_class = ParquetWriter

    @overrides
    def _write_files_to_new_table(
        self,
        files: list[Path],
        stream_name: str,
        batch_id: str,
    ) -> str:
        """Write a file(s) to a new table.

        TODO: Override the base implementation to use the COPY command.
        """
        return super()._write_files_to_new_table(files, stream_name, batch_id)
