"""A SQL Cache implementation."""

import abc
from pathlib import Path
from textwrap import dedent
from typing import final, Iterable
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
    """Same as a regular config except it exposes the 'get_sql_alchemy_url()' method."""

    dedupe_mode = RecordDedupeMode.APPEND
    schema: str
    table_prefix: str
    table_suffix: str

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
    config_class: type[SQLCacheConfigBase] = SQLCacheConfigBase

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
        """Return the SQLAlchemy URL to use."""
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
        return self.normalize_table_name(f"{stream_name}_{batch_id}")

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
        stream_name: str,
        batch_id: str,
    ) -> str:
        """Create a new table for loading data."""
        temp_table_name = self.get_temp_table_name(stream_name, batch_id)
        column_definition_str = ",\n  ".join(
            f"{column_name} {sql_type}" for column_name, sql_type in self.get_sql_column_definitions(stream_name).items()
        )
        self._create_table(temp_table_name, column_definition_str)

    def ensure_final_table_exists(
        self,
        stream_name: str,
        create_if_missing: True,
    ) -> str:
        """
        Create the final table if it doesn't already exist.

        Return the table name.
        """
        table_name = self.get_final_table_name(stream_name)
        did_exist = self.table_exists(table_name)
        if not did_exist and create_if_missing:
            column_definition_str = ",\n  ".join(
                f"{column_name} {sql_type}" for column_name, sql_type in self.get_sql_column_definitions(stream_name).items()
            )
            self._create_table(table_name, column_definition_str)

        return table_name

    @final
    def _create_table(
        self,
        table_name: str,
        column_definition_str: str,
    ) -> None:
        with self.get_sql_engine().begin() as conn:
            conn.execute(
                dedent(
                    f"""
                    CREATE TABLE {table_name} (
                      {column_definition_str}
                    )
                    """
                )
            )

    def normalize_column_name(
        self,
        raw_name,
    ):
        return raw_name.lower().replace(" ", "_").replace("-", "_")

    def normalize_table_name(
        self,
        raw_name,
    ):
        return raw_name.lower().replace(" ", "_").replace("-", "_")

    @final
    def get_sql_column_definitions(
        self,
        stream_name: str,
    ) -> dict[str, sqlalchemy.sql.sqltypes.TypeEngine]:
        """Return the column definitions for the given stream."""
        columns = {
            self.normalize_column_name(property_name): self.type_converter.to_sql_type(json_schema)
            for property_name, json_schema in self.get_stream_json_schema(stream_name)["properties"].items()
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
        self.write_files_to_new_table(files, temp_table_name)
        final_table_name = self.ensure_final_table_exists(stream_name, create_if_missing=True)
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

    @final
    def write_temp_table_to_final_table(
        self,
        temp_table_name: str,
        final_table_name: str,
    ) -> None:
        """Merge the temp table into the final table."""
        if self.config.dedupe_mode == RecordDedupeMode.REPLACE:
            if not self.supports_merge_insert:
                raise NotImplementedError("Deduping was requested but merge-insert is not yet supported.")

            self.merge_temp_table_to_final_table(temp_table_name, final_table_name)

        else:
            self.append_temp_table_to_final_table(temp_table_name, final_table_name)

    def append_temp_table_to_final_table(
        self,
        temp_table_name,
        final_table_name,
        stream_name,
    ):
        nl = "\n"
        columns = self.get_sql_column_definitions(stream_name).keys()
        with self.get_sql_engine().begin() as conn:
            conn.execute(
                f"""
                INSERT INTO {final_table_name} (
                  {f',{nl}  '.join(columns)}
                )
                SELECT
                  {f',{nl}  '.join(columns)}
                FROM {temp_table_name}
                """
            )

    def get_primary_keys(
        self,
        stream_name: str,
    ) -> list[str]:
        # TODO: get primary key declarations from the catalog
        return []

    def merge_temp_table_to_final_table(
        self,
        temp_table_name: str,
        final_table_name: str,
        stream_name: str,
    ):
        """Merge the temp table into the main one.

        This implementation requires MERGE support in the SQL DB.
        Databases that do not support this syntax can override this method.
        """
        nl = "\n"
        columns = self.get_sql_column_definitions(stream_name).keys()
        pk_columns = self.get_primary_keys(stream_name)
        non_pk_columns = columns - pk_columns
        join_clause = "{nl} AND ".join(f"tmp.{pk_col} = final.{pk_col}" for pk_col in pk_columns)
        set_clause = "{nl}    ".join(f"{col} = tmp.{col}" for col in non_pk_columns)
        with self.get_sql_engine().begin() as conn:
            conn.execute(
                f"""
                MERGE INTO {final_table_name} final
                USING (
                  SELECT *
                  FROM {temp_table_name}
                ) AS tmp
                 ON {join_clause}
                WHEN MATCHED THEN UPDATE
                  SET
                    {set_clause}
                WHEN NOT MATCHED THEN INSERT
                  (
                    {f',{nl}    '.join(columns)}
                  )
                  VALUES (
                    tmp.{f',{nl}    tmp.'.join(columns)}
                  );
                """
            )

    @final
    def table_exists(
        self,
        table_name: str,
    ) -> bool:
        return sqlalchemy.inspect(self.create_engine()).has_table(table_name)

    def get_final_table_name(
        self,
        stream_name: str,
    ) -> str:
        """Return the name of the SQL table for the given stream."""
        return self.normalize_table_name(
            f"{self.config.table_prefix}{stream_name}{self.config.table_suffix}",
        )

    def read_all(
        self,
        stream_name: str,
    ) -> Iterable[sqlalchemy.Row]:
        """Uses SQLAlchemy to select all rows from the table."""
        table_name = self.get_final_table_name(stream_name)
        engine = self.create_engine()
        stmt = sqlalchemy.select(table_name)
        with engine.connect() as conn:
            yield from conn.execute(stmt)
