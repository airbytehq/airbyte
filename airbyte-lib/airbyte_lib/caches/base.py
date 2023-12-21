"""A SQL Cache implementation."""

import abc
from pathlib import Path
from textwrap import dedent
from typing import final, Iterable, Any, cast
import enum

import pandas as pd
import pyarrow as pa
import ulid
import sqlalchemy
from sqlalchemy import text
from overrides import overrides

from airbyte_lib.config import CacheConfigBase
from airbyte_lib.processors import RecordProcessor, BatchHandle

from airbyte_lib.types import SQLTypeConverter
from airbyte_lib.file_writers import FileWriterBase

class RecordDedupeMode(enum.Enum):
    APPEND = "append"
    REPLACE = "replace"


class SQLCacheConfigBase(CacheConfigBase):
    """Same as a regular config except it exposes the 'get_sql_alchemy_url()' method."""

    dedupe_mode = RecordDedupeMode.APPEND
    schema_name: str = "airbyte_raw"
    table_prefix: str = ""
    table_suffix: str = ""

    @abc.abstractmethod
    def get_sql_alchemy_url(self):
        """Returns a SQL Alchemy URL."""


class GenericSQLCacheConfig(SQLCacheConfigBase):
    """Allows configuring 'sql_alchemy_url' directly."""

    sql_alchemy_url: str

    @overrides
    def get_sql_alchemy_url(self):
        """Returns a SQL Alchemy URL."""
        return self.sql_alchemy_url


class SQLCacheBase(RecordProcessor):
    """A base class to be used for SQL Caches.

    Optionally we can use a file cache to store the data in parquet files.
    """

    type_converter_class = SQLTypeConverter
    config_class: type[SQLCacheConfigBase]
    file_writer_class: type[FileWriterBase]

    supports_merge_insert = False

    # Constructor:

    @final  # We don't want subclasses to have to override the constructor.
    def __init__(
        self,
        config: SQLCacheConfigBase,
        source_catalog: dict[str, Any],  # TODO: Better typing for ConfiguredAirbyteCatalog
        file_writer: FileWriterBase | None = None,
        **kwargs,  # Added for future proofing purposes.
    ):
        self.config: SQLCacheConfigBase
        super().__init__(config, source_catalog, **kwargs)

        self.file_writer = file_writer or self.file_writer_class(
            config,
            source_catalog=source_catalog
        )
        self.type_converter = self.type_converter_class()

    # Public interface:

    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        return self.config.get_sql_alchemy_url()

    @final
    def get_sql_engine(self) -> sqlalchemy.engine.Engine:
        """Return a new SQL engine to use."""
        return sqlalchemy.create_engine(self.get_sql_alchemy_url())

    def get_sql_table_name(
        self,
        stream_name: str,
    ) -> str:
        """Return the name of the SQL table for the given stream."""
        return self._normalize_table_name(
            f"{self.config.table_prefix}{stream_name}{self.config.table_suffix}",
        )

    @final
    def get_sql_table(
        self,
        stream_name: str,
    ) -> sqlalchemy.Table:
        """Return a temporary table name."""
        table_name = self.get_sql_table_name(stream_name)
        return sqlalchemy.Table(
            table_name,
            sqlalchemy.MetaData(schema=self.config.schema_name),
            autoload=True,  # Retrieve the table definition from the database
            autoload_with=self.get_sql_engine(),
        )

    # Read methods:

    def read_all(
        self,
        stream_name: str,
    ) -> Iterable[dict[str, Any]]:
        """Uses SQLAlchemy to select all rows from the table."""
        table_ref = self.get_sql_table(stream_name)
        engine = self.get_sql_engine()
        stmt = table_ref.select()
        with engine.connect() as conn:
            yield from conn.execute(stmt)

    def read_all_as_pandas(
        self,
        stream_name: str,
    ) -> pd.DataFrame:
        """Return a Pandas data frame with the stream's data."""
        table_name = self.get_sql_table_name(stream_name)
        engine = self.get_sql_engine()
        return pd.read_sql_table(table_name, engine)

    # Protected members (non-public interface):

    @final
    def _get_temp_table_name(
        self,
        stream_name: str,
        batch_id: str | None = None,  # ULID of the batch
    ) -> str:
        """Return a new (unique) temporary table name."""
        batch_id = batch_id or str(ulid.ULID())
        return self._normalize_table_name(f"{stream_name}_{batch_id}")

    @final
    def _create_table_for_loading(
        self,
        /,
        stream_name: str,
        batch_id: str,
    ) -> str:
        """Create a new table for loading data."""
        temp_table_name = self._get_temp_table_name(stream_name, batch_id)
        column_definition_str = ",\n  ".join(
            f"{column_name} {sql_type}"
            for column_name, sql_type in self._get_sql_column_definitions(
                stream_name
            ).items()
        )
        self._create_table(temp_table_name, column_definition_str)

        return temp_table_name

    def _ensure_final_table_exists(
        self,
        stream_name: str,
        create_if_missing: bool = True,
    ) -> str:
        """
        Create the final table if it doesn't already exist.

        Return the table name.
        """
        table_name = self.get_sql_table_name(stream_name)
        did_exist = self._table_exists(table_name)
        if not did_exist and create_if_missing:
            column_definition_str = ",\n  ".join(
                f"{column_name} {sql_type}"
                for column_name, sql_type in self._get_sql_column_definitions(
                    stream_name
                ).items()
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
            conn.execute(text(dedent(
                f"""
                CREATE TABLE {table_name} (
                    {column_definition_str}
                )
                """
            )))

    def _normalize_column_name(
        self,
        raw_name,
    ):
        return raw_name.lower().replace(" ", "_").replace("-", "_")

    def _normalize_table_name(
        self,
        raw_name,
    ):
        return raw_name.lower().replace(" ", "_").replace("-", "_")

    @final
    def _get_sql_column_definitions(
        self,
        stream_name: str,
    ) -> dict[str, sqlalchemy.sql.sqltypes.TypeEngine]:
        """Return the column definitions for the given stream."""
        columns: dict[str, sqlalchemy.sql.sqltypes.TypeEngine] = {}
        properties = cast(dict[str, dict[str, str | dict]], self._get_stream_json_schema(stream_name)["properties"])
        for property_name, json_schema_property_def in properties.items():
            clean_prop_name = self._normalize_column_name(property_name)
            columns[clean_prop_name] = self.type_converter.to_sql_type(json_schema_property_def)

        # Add the metadata columns
        columns["_airbyte_extracted_at"] = sqlalchemy.TIMESTAMP()
        columns["_airbyte_loaded_at"] = sqlalchemy.TIMESTAMP()
        return columns

    @final
    def _get_stream_json_schema(
        self,
        stream_name: str,
    ) -> dict[str, str | dict[str, str | dict]]:
        """Return the column definitions for the given stream."""
        return self.source_catalog["streams"][stream_name]["json_schema"]

    @overrides
    def _write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table | pa.RecordBatch,
    ) -> Path:
        """
        Process a record batch.

        Return the path to the cache file.
        """
        return self.file_writer._write_batch(stream_name, batch_id, record_batch)

    @final
    @overrides
    def _finalize_batches(self, stream_name: str) -> dict[str, BatchHandle]:
        """Finalize all uncommitted batches.

        If a stream name is provided, only process uncommitted batches for that stream.

        This is a generic 'final' implementation, which should not be overridden by subclasses.

        Returns a mapping of batch IDs to batch handles, for those batches that were processed.
        """
        batches_to_finalize = self._pending_batches[stream_name]

        if not batches_to_finalize:
            return {}

        # Get a list of all files to finalize from all pending batches.
        files: list[Path] = [
            file_path for batch_handle
            in cast(list[list[Path]], batches_to_finalize.values())
            for file_path in batch_handle
        ]
        # Use the max batch ID as the batch ID for table names.
        max_batch_id = max(batches_to_finalize.keys())
        temp_table_name = self._write_files_to_new_table(files, stream_name, max_batch_id)

        # TODO: Add a dedupe step here to remove duplicates from the temp table.
        #       Some sources will send us duplicate records within the same stream,
        #       although this is a fairly rare edge case we can ignore in V1.

        # Merge to final table
        final_table_name = self._ensure_final_table_exists(
            stream_name, create_if_missing=True
        )
        self._write_temp_table_to_final_table(stream_name, temp_table_name, final_table_name)

        # Drop the temp table and do some cleanup
        self._drop_temp_table(temp_table_name)
        self._completed_batches.update(batches_to_finalize)
        self._pending_batches.clear()

        # Return the batch handles as measure of work completed.
        return batches_to_finalize


    def _drop_temp_table(
        self,
        table_name: str,
    ) -> None:
        """Drop the given table."""
        with self.get_sql_engine().begin() as conn:
            conn.execute(text(f"DROP TABLE {table_name}"))

    def _write_files_to_new_table(
        self,
        files: list[Path],
        stream_name: str,
        batch_id: str,
    ) -> str:
        """Write a file(s) to a new table.

        This is a generic implementation, which can be overridden by subclasses
        to improve performance.
        """
        temp_table_name = self._create_table_for_loading(stream_name, batch_id)
        for file_path in files:
            with pa.parquet.ParquetFile(file_path) as pf:
                record_batch = pf.read()
                record_batch.to_pandas().to_sql(
                    temp_table_name,
                    self.get_sql_alchemy_url(),
                    if_exists="replace",
                    index=False,
                )
        return temp_table_name

    @final
    def _write_temp_table_to_final_table(
        self,
        stream_name: str,
        temp_table_name: str,
        final_table_name: str,
    ) -> None:
        """Merge the temp table into the final table."""
        if self.config.dedupe_mode == RecordDedupeMode.REPLACE:
            if not self.supports_merge_insert:
                raise NotImplementedError(
                    "Deduping was requested but merge-insert is not yet supported."
                )

            self._merge_temp_table_to_final_table(stream_name, temp_table_name, final_table_name)

        else:
            self._append_temp_table_to_final_table(stream_name, temp_table_name, final_table_name)

    def _append_temp_table_to_final_table(
        self,
        temp_table_name,
        final_table_name,
        stream_name,
    ):
        nl = "\n"
        columns = self._get_sql_column_definitions(stream_name).keys()
        with self.get_sql_engine().begin() as conn:
            conn.execute(
                text(
                    f"""
                    INSERT INTO {final_table_name} (
                    {f',{nl}  '.join(columns)}
                    )
                    SELECT
                    {f',{nl}  '.join(columns)}
                    FROM {temp_table_name}
                    """
                )
            )

    def _get_primary_keys(
        self,
        stream_name: str,
    ) -> list[str]:
        # TODO: get primary key declarations from the catalog
        return []

    def _merge_temp_table_to_final_table(
        self,
        stream_name: str,
        temp_table_name: str,
        final_table_name: str,
    ):
        """Merge the temp table into the main one.

        This implementation requires MERGE support in the SQL DB.
        Databases that do not support this syntax can override this method.
        """
        nl = "\n"
        columns = self._get_sql_column_definitions(stream_name).keys()
        pk_columns = self._get_primary_keys(stream_name)
        non_pk_columns = columns - pk_columns
        join_clause = "{nl} AND ".join(
            f"tmp.{pk_col} = final.{pk_col}" for pk_col in pk_columns
        )
        set_clause = "{nl}    ".join(f"{col} = tmp.{col}" for col in non_pk_columns)
        with self.get_sql_engine().begin() as conn:
            conn.execute(
                text(
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
            )

    @final
    def _table_exists(
        self,
        table_name: str,
    ) -> bool:
        return sqlalchemy.inspect(self.get_sql_engine()).has_table(table_name)
