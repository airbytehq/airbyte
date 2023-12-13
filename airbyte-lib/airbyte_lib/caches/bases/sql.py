"""A SQL Cache implementation."""

import abc
from pathlib import Path
from typing import final
import enum

import pyarrow as pa
import ulid
import sqlalchemy
from overrides import overrides

from .base import BaseCache, BatchHandle
from .config import CacheConfigBase

from airbyte_lib.type_converters import SQLTypeConverterBase


class RecordDedupeMode(enum.Enum):
    APPEND = "append"
    REPLACE = "replace"


class SQLCacheConfigBase(CacheConfigBase):
    """Same as a regular config except it exposes an additional 'sql_alchemy_url' property."""

    dedupe_mode = RecordDedupeMode.APPEND

    @abc.abstractmethod
    def get_sql_alchemy_url(self):
        """Returns a SQL Alchemy URL."""


class GenericSQLCacheConfig(SQLCacheConfigBase):
    """Allows configuring 'sql_alchemy_url' directly."""

    sql_alchemy_url: str

    @overrides
    def get_sql_alchemy_url(self):
        """Returns a SQL Alchemy URL."""
        return self.custom_sql_alchemy_url


class SQLCache(BaseCache, abc.ABCMeta):
    """A base class to be used for SQL Caches.

    Optionally we can use a file cache to store the data in parquet files.
    """

    type_converter_class = SQLTypeConverterBase
    supports_merge_insert = False

    def __init__(
        self,
        config: CacheConfigBase,  # Configuration for the SQL cache
        file_cache: BaseCache | None = None,
        **kwargs,  # Added for future proofing purposes.
    ):
        self.config = config
        self.file_cache = file_cache
        self.type_converter = self.type_converter_class()

    def get_sql_alchemy_url(self) -> str:
        """Return the SQL alchemy URL to use."""
        return self.config.sql_alchemy_url

    @final
    def create_engine(self) -> sqlalchemy.engine.Engine:
        """Return a new SQL engine to use."""
        return sqlalchemy.create_engine(self.get_sql_alchemy_url(self.config))

    @final
    def get_temp_table_name(
        self,
        stream_name: str,
        batch_id: str | None = None,  # ULID of the batch
    ) -> str:
        """Return a new (unique) temporary table name."""
        batch_id = batch_id or ulid.new().str
        return f"{stream_name}_{batch_id}"

    @final
    def get_table_ref(
        self,
        table_name: str | None = None,
        schema_name: str | None = None,
        auto_load: bool = True,  # Whether to auto-load the table
    ) -> sqlalchemy.Table:
        """Return a temporary table name."""
        return sqlalchemy.Table(
            table_name,
            sqlalchemy.MetaData(schema=schema_name),
            autoload=auto_load,
            autoload_with=self.get_sql_engine(),
        )

    @final
    def create_table_for_loading(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> str:
        """Create a new table for loading data."""
        column_definition_str = ",\n".join(
            f"{column_name} {sql_type}," for column_name, sql_type in self.get_sql_column_definitions(table_name).items()
        )
        with self.get_sql_engine().begin() as conn:
            conn.execute(
                f"""
                CREATE TABLE {schema_name}.{table_name} (
                    {column_definition_str}
                )
                """
            )
        return table_name

    @final
    def get_sql_column_definitions(
        self,
        stream_name: str,
    ) -> dict[str, sqlalchemy.sql.sqltypes.TypeEngine]:
        """Return the column definitions for the given stream."""
        columns = {
            column_name: self.type_converter.to_sql_type(json_schema)
            for column_name, json_schema in self.get_stream_json_schema(stream_name)["properties"].items()
        }
        # Add the metadata columns
        columns["_airbyte_extracted_at"] = sqlalchemy.TIMESTAMP
        columns["_airbyte_loaded_at"] = sqlalchemy.TIMESTAMP
        return columns

    @final
    def get_stream_json_schema(
        self,
        stream_name: str,
    ) -> dict[str, str]:
        """Return the column definitions for the given stream."""
        return self.catalog.streams[stream_name]["json_schema"]

    @final
    @overrides
    def finalize_batches(self, stream_name: str, batches: dict[str, BatchHandle]) -> bool:
        """Finalize all uncommitted batches.

        If a stream name is provided, only process uncommitted batches for that stream.
        """
        files: list[Path] = [batch_handle for batch_handle in batches.values()]
        max_batch_id = max(batches.keys())
        temp_table_name = self.get_temp_table_name(
            stream_name,
            batch_id=max_batch_id,
        )
        final_table_name = self.get_final_table_name(stream_name)
        self.write_files_to_new_table(files, temp_table_name)
        self.write_temp_table_to_final_table(temp_table_name, final_table_name)
        self._drop_temp_table(temp_table_name)

    def _drop_temp_table(
        self,
        table_name: str,
    ) -> None:
        """Drop the given table."""
        with self.get_sql_engine().begin() as conn:
            conn.execute(
                f"""
                DROP TABLE {table_name};
                """
            )

    def write_files_to_new_table(
        self,
        files: list[Path],
        table_name: str,
    ) -> None:
        """Write a file(s) to a new table.

        This is a generic implementation, which can be overridden by subclasses
        to improve performance.
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

    def write_temp_table_to_final_table(
        self,
        temp_table_name: str,
        final_table_name: str,
    ) -> None:
        """Merge the temp table into the final table."""
        if self.config.dedupe_mode == RecordDedupeMode.REPLACE:
            if not self.supports_merge_insert:
                raise NotImplementedError("Deduping was requested but merge-insert is not yet supported.")

            assert False  # Not reachable
            # TODO: Add a generic merge upsert here

        else:  # RecordDedupeMode.APPEND
            with self.get_sql_engine().begin() as conn:
                conn.execute(
                    f"""
                    INSERT INTO {final_table_name}
                    SELECT * FROM {temp_table_name}
                    """
                )

    def get_final_table_name(
        self,
        stream_name: str,
    ) -> str:
        """Return the name of the SQL table for the given stream."""
        return f"{stream_name}"
