"""A Snowflake implementation of the cache."""

from __future__ import annotations

from pathlib import Path

from overrides import overrides
import pyarrow as pa

from airbyte_lib.caches.bases import SQLCache, SQLCacheConfigBase
from airbyte_lib.file_writers import ParquetWriter, ParquetWriterConfig


class SnowflakeCacheConfig(SQLCacheConfigBase, ParquetWriterConfig):
    """Configuration for the Snowflake cache.

    Also inherits config from the ParquetWriter, which is responsible for writing files to disk.
    """

    type: str = "snowflake"
    account: str
    username: str
    password: str
    warehouse: str
    database: str

    # Already defined in base class:
    # schema: str

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        return (
            f"snowflake://{self.username}:{self.password}@{self.account}/"
            f"?warehouse={self.warehouse}&database={self.database}&schema={self.schema}"
        )


class SnowflakeSQLCache(SQLCache):
    """A Snowflake implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    """

    config_class = SnowflakeCacheConfig
    file_writer_class = ParquetWriter

    @overrides
    def write_files_to_new_table(
        self,
        files: list[Path],
        table_name: str,
    ) -> None:
        """Write a file(s) to a new table.

        TODO: Override the base implementation to use the COPY command.
        """
        self.create_table_for_loading(table_name)
        for file_path in files:
            with pa.parquet.ParquetFile(file_path) as pf:
                record_batch = pf.read()
                record_batch.to_pandas().to_sql(
                    table_name,
                    self.get_sql_alchemy_url(),
                    if_exists="replace",
                    index=False,
                )
