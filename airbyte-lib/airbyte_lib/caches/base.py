# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A SQL Cache implementation."""

import abc
import enum
from collections.abc import Generator, Iterator, Mapping
from contextlib import contextmanager
from functools import cached_property, lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast, final

import pandas as pd
import pyarrow as pa
import sqlalchemy
import ulid
from overrides import overrides
from sqlalchemy import CursorResult, Executable, TextClause, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from airbyte_protocol.models import ConfiguredAirbyteStream

from airbyte_lib._file_writers.base import FileWriterBase, FileWriterBatchHandle
from airbyte_lib._processors import BatchHandle, RecordProcessor
from airbyte_lib.config import CacheConfigBase
from airbyte_lib.types import SQLTypeConverter


if TYPE_CHECKING:
    from sqlalchemy.engine import Connection
    from sqlalchemy.engine.reflection import Inspector

    from airbyte_lib.datasets._base import DatasetBase


DEBUG_MODE = False  # Set to True to enable additional debug logging.


class RecordDedupeMode(enum.Enum):
    APPEND = "append"
    REPLACE = "replace"


class SQLRuntimeError(Exception):
    """Raised when an SQL operation fails."""


class SQLCacheConfigBase(CacheConfigBase):
    """Same as a regular config except it exposes the 'get_sql_alchemy_url()' method."""

    dedupe_mode = RecordDedupeMode.REPLACE
    schema_name: str = "airbyte_raw"

    table_prefix: str | None = None
    """ A prefix to add to all table names.
    If 'None', a prefix will be created based on the source name.
    """

    table_suffix: str = ""
    """A suffix to add to all table names."""

    @abc.abstractmethod
    def get_sql_alchemy_url(self) -> str:
        """Returns a SQL Alchemy URL."""
        ...

    @abc.abstractmethod
    def get_database_name(self) -> str:
        """Return the name of the database."""
        ...


class GenericSQLCacheConfig(SQLCacheConfigBase):
    """Allows configuring 'sql_alchemy_url' directly."""

    sql_alchemy_url: str

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Returns a SQL Alchemy URL."""
        return self.sql_alchemy_url


class SQLCacheBase(RecordProcessor):
    """A base class to be used for SQL Caches.

    Optionally we can use a file cache to store the data in parquet files.
    """

    type_converter_class: type[SQLTypeConverter] = SQLTypeConverter
    config_class: type[SQLCacheConfigBase]
    file_writer_class: type[FileWriterBase]

    supports_merge_insert = False
    use_singleton_connection = False  # If true, the same connection is used for all operations.

    # Constructor:

    @final  # We don't want subclasses to have to override the constructor.
    def __init__(
        self,
        config: SQLCacheConfigBase | None = None,
        file_writer: FileWriterBase | None = None,
        **kwargs: dict[str, Any],  # Added for future proofing purposes.
    ) -> None:
        self.config: SQLCacheConfigBase
        self._engine: Engine | None = None
        self._connection_to_reuse: Connection | None = None
        super().__init__(config, **kwargs)
        self._ensure_schema_exists()

        self.file_writer = file_writer or self.file_writer_class(config)
        self.type_converter = self.type_converter_class()

    # Public interface:

    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        return self.config.get_sql_alchemy_url()

    @final
    @cached_property
    def database_name(self) -> str:
        """Return the name of the database."""
        return self.config.get_database_name()

    @final
    def get_sql_engine(self) -> Engine:
        """Return a new SQL engine to use."""
        if self._engine:
            return self._engine

        sql_alchemy_url = self.get_sql_alchemy_url()
        if self.use_singleton_connection:
            if self._connection_to_reuse is None:
                # This temporary bootstrap engine will be created once and is needed to
                # create the long-lived connection object.
                bootstrap_engine = create_engine(
                    sql_alchemy_url,
                )
                self._connection_to_reuse = bootstrap_engine.connect()

            self._engine = create_engine(
                sql_alchemy_url,
                creator=lambda: self._connection_to_reuse,
                poolclass=StaticPool,
                echo=DEBUG_MODE,
                # isolation_level="AUTOCOMMIT",
            )
        else:
            # Regular engine creation for new connections
            self._engine = create_engine(
                sql_alchemy_url,
                echo=DEBUG_MODE,
                # isolation_level="AUTOCOMMIT",
            )

        return self._engine

    @contextmanager
    def get_sql_connection(self) -> Generator[sqlalchemy.engine.Connection, None, None]:
        """A context manager which returns a new SQL connection for running queries.

        If the connection needs to close, it will be closed automatically.
        """
        if self.use_singleton_connection and self._connection_to_reuse is not None:
            connection = self._connection_to_reuse
            yield connection

        else:
            with self.get_sql_engine().begin() as connection:
                yield connection

        if not self.use_singleton_connection:
            connection.close()
            del connection

    def get_sql_table_name(
        self,
        stream_name: str,
    ) -> str:
        """Return the name of the SQL table for the given stream."""
        table_prefix = self.config.table_prefix or ""

        # TODO: Add default prefix based on the source name.

        return self._normalize_table_name(
            f"{table_prefix}{stream_name}{self.config.table_suffix}",
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
            autoload_with=self.get_sql_engine(),
        )

    @final
    @property
    def streams(
        self,
    ) -> dict[str, "DatasetBase"]:
        """Return a temporary table name."""
        # TODO: Add support for streams map, based on the cached catalog.
        raise NotImplementedError("Streams map is not yet supported.")

    # Read methods:

    def get_records(
        self,
        stream_name: str,
    ) -> Iterator[Mapping[str, Any]]:
        """Uses SQLAlchemy to select all rows from the table.

        # TODO: Refactor to return a LazyDataset here.
        """
        table_ref = self.get_sql_table(stream_name)
        stmt = table_ref.select()
        with self.get_sql_connection() as conn:
            for row in conn.execute(stmt):
                # Access to private member required because SQLAlchemy doesn't expose a public API.
                # https://pydoc.dev/sqlalchemy/latest/sqlalchemy.engine.row.RowMapping.html
                yield cast(Mapping[str, Any], row._mapping)  # noqa: SLF001

    def get_pandas_dataframe(
        self,
        stream_name: str,
    ) -> pd.DataFrame:
        """Return a Pandas data frame with the stream's data."""
        table_name = self.get_sql_table_name(stream_name)
        engine = self.get_sql_engine()
        return pd.read_sql_table(table_name, engine)

    # Protected members (non-public interface):

    def _ensure_schema_exists(
        self,
    ) -> None:
        """Return a new (unique) temporary table name."""
        schema_name = self.config.schema_name
        if schema_name in self._get_schemas_list():
            return

        sql = f"CREATE SCHEMA IF NOT EXISTS {schema_name}"

        try:
            self._execute_sql(sql)
        except Exception as ex:  # noqa: BLE001 # Too-wide catch because we don't know what the DB will throw.
            # Ignore schema exists errors.
            if "already exists" not in str(ex):
                raise

        if DEBUG_MODE:
            found_schemas = self._get_schemas_list()
            assert (
                schema_name in found_schemas
            ), f"Schema {schema_name} was not created. Found: {found_schemas}"

    @final
    def _get_temp_table_name(
        self,
        stream_name: str,
        batch_id: str | None = None,  # ULID of the batch
    ) -> str:
        """Return a new (unique) temporary table name."""
        batch_id = batch_id or str(ulid.ULID())
        return self._normalize_table_name(f"{stream_name}_{batch_id}")

    def _fully_qualified(
        self,
        table_name: str,
    ) -> str:
        """Return the fully qualified name of the given table."""
        # return f"{self.database_name}.{self.config.schema_name}.{table_name}"
        return f"{self.config.schema_name}.{table_name}"

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
            for column_name, sql_type in self._get_sql_column_definitions(stream_name).items()
        )
        self._create_table(temp_table_name, column_definition_str)

        return temp_table_name

    def _get_tables_list(
        self,
    ) -> list[str]:
        """Return a list of all tables in the database."""
        with self.get_sql_connection() as conn:
            inspector: Inspector = sqlalchemy.inspect(conn)
            return inspector.get_table_names(schema=self.config.schema_name)

    def _get_schemas_list(
        self,
        database_name: str | None = None,
    ) -> list[str]:
        """Return a list of all tables in the database."""
        inspector: Inspector = sqlalchemy.inspect(self.get_sql_engine())
        database_name = database_name or self.database_name
        found_schemas = inspector.get_schema_names()
        return [
            found_schema.split(".")[-1].strip('"')
            for found_schema in found_schemas
            if "." not in found_schema
            or (found_schema.split(".")[0].lower().strip('"') == database_name.lower())
        ]

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
                    stream_name,
                ).items()
            )
            self._create_table(table_name, column_definition_str)

        return table_name

    def _ensure_compatible_table_schema(
        self,
        stream_name: str,
        table_name: str,
        raise_on_error: bool = False,
    ) -> bool:
        """Return true if the given table is compatible with the stream's schema.

        If raise_on_error is true, raise an exception if the table is not compatible.

        TODO: Expand this to check for column types and sizes, and to add missing columns.

        Returns true if the table is compatible, false if it is not.
        """
        json_schema = self._get_stream_json_schema(stream_name)
        stream_column_names: list[str] = json_schema["properties"].keys()
        table_column_names: list[str] = self.get_sql_table(table_name).columns.keys()

        missing_columns: set[str] = set(stream_column_names) - set(table_column_names)
        if missing_columns:
            if raise_on_error:
                raise RuntimeError(
                    f"Table {table_name} is missing columns: {missing_columns}",
                )
            return False  # Some columns are missing.

        return True  # All columns exist.

    @final
    def _create_table(
        self,
        table_name: str,
        column_definition_str: str,
    ) -> None:
        if DEBUG_MODE:
            assert table_name not in self._get_tables_list(), f"Table {table_name} already exists."

        cmd = f"""
        CREATE TABLE {self._fully_qualified(table_name)} (
            {column_definition_str}
        )
        """
        _ = self._execute_sql(cmd)
        if DEBUG_MODE:
            tables_list = self._get_tables_list()
            assert (
                table_name in tables_list
            ), f"Table {table_name} was not created. Found: {tables_list}"

    def _normalize_column_name(
        self,
        raw_name: str,
    ) -> str:
        return raw_name.lower().replace(" ", "_").replace("-", "_")

    def _normalize_table_name(
        self,
        raw_name: str,
    ) -> str:
        return raw_name.lower().replace(" ", "_").replace("-", "_")

    @final
    def _get_sql_column_definitions(
        self,
        stream_name: str,
    ) -> dict[str, sqlalchemy.types.TypeEngine]:
        """Return the column definitions for the given stream."""
        columns: dict[str, sqlalchemy.types.TypeEngine] = {}
        properties = self._get_stream_json_schema(stream_name)["properties"]
        for property_name, json_schema_property_def in properties.items():
            clean_prop_name = self._normalize_column_name(property_name)
            columns[clean_prop_name] = self.type_converter.to_sql_type(
                json_schema_property_def,
            )

        # TODO: Add the metadata columns (this breaks tests)
        # columns["_airbyte_extracted_at"] = sqlalchemy.TIMESTAMP()
        # columns["_airbyte_loaded_at"] = sqlalchemy.TIMESTAMP()
        return columns

    @final
    def _get_stream_config(
        self,
        stream_name: str,
    ) -> ConfiguredAirbyteStream:
        """Return the column definitions for the given stream."""
        if not self.source_catalog:
            raise RuntimeError("Cannot get stream JSON schema without a catalog.")

        matching_streams: list[ConfiguredAirbyteStream] = [
            stream for stream in self.source_catalog.streams if stream.stream.name == stream_name
        ]
        if not matching_streams:
            raise RuntimeError(f"Stream '{stream_name}' not found in catalog.")

        if len(matching_streams) > 1:
            raise RuntimeError(f"Multiple streams found with name '{stream_name}'.")

        return matching_streams[0]

    @final
    def _get_stream_json_schema(
        self,
        stream_name: str,
    ) -> dict[str, Any]:
        """Return the column definitions for the given stream."""
        return self._get_stream_config(stream_name).stream.json_schema

    @overrides
    def _write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table | pa.RecordBatch,
    ) -> FileWriterBatchHandle:
        """
        Process a record batch.

        Return the path to the cache file.
        """
        return self.file_writer.write_batch(stream_name, batch_id, record_batch)

    def _cleanup_batch(
        self,
        stream_name: str,
        batch_id: str,
        batch_handle: BatchHandle,
    ) -> None:
        """Clean up the cache.

        For SQL caches, we only need to call the cleanup operation on the file writer.

        Subclasses should call super() if they override this method.
        """
        self.file_writer.cleanup_batch(stream_name, batch_id, batch_handle)

    @final
    @overrides
    def _finalize_batches(self, stream_name: str) -> dict[str, BatchHandle]:
        """Finalize all uncommitted batches.

        This is a generic 'final' implementation, which should not be overridden.

        Returns a mapping of batch IDs to batch handles, for those processed batches.

        TODO: Add a dedupe step here to remove duplicates from the temp table.
              Some sources will send us duplicate records within the same stream,
              although this is a fairly rare edge case we can ignore in V1.
        """
        with self._finalizing_batches(stream_name) as batches_to_finalize:
            if not batches_to_finalize:
                return {}

            files: list[Path] = []
            # Get a list of all files to finalize from all pending batches.
            for batch_handle in batches_to_finalize.values():
                batch_handle = cast(FileWriterBatchHandle, batch_handle)
                files += batch_handle.files
            # Use the max batch ID as the batch ID for table names.
            max_batch_id = max(batches_to_finalize.keys())

            # Make sure the target schema and target table exist.
            self._ensure_schema_exists()
            final_table_name = self._ensure_final_table_exists(
                stream_name,
                create_if_missing=True,
            )
            self._ensure_compatible_table_schema(
                stream_name=stream_name,
                table_name=final_table_name,
                raise_on_error=True,
            )

            try:
                temp_table_name = self._write_files_to_new_table(
                    files,
                    stream_name,
                    max_batch_id,
                )
                self._write_temp_table_to_final_table(
                    stream_name,
                    temp_table_name,
                    final_table_name,
                )
            finally:
                self._drop_temp_table(temp_table_name, if_exists=True)

            # Return the batch handles as measure of work completed.
            return batches_to_finalize

    def _execute_sql(self, sql: str | TextClause | Executable) -> CursorResult:
        """Execute the given SQL statement."""
        if isinstance(sql, str):
            sql = text(sql)
        if isinstance(sql, TextClause):
            sql = sql.execution_options(
                autocommit=True,
            )

        with self.get_sql_connection() as conn:
            try:
                result = conn.execute(sql)
            except (
                sqlalchemy.exc.ProgrammingError,
                sqlalchemy.exc.SQLAlchemyError,
            ) as ex:
                msg = f"Error when executing SQL:\n{sql}\n{type(ex).__name__}{ex!s}"
                raise SQLRuntimeError(msg) from None  # from ex

        return result

    def _drop_temp_table(
        self,
        table_name: str,
        if_exists: bool = True,
    ) -> None:
        """Drop the given table."""
        exists_str = "IF EXISTS" if if_exists else ""
        self._execute_sql(f"DROP TABLE {exists_str} {self._fully_qualified(table_name)}")

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
                dataframe = record_batch.to_pandas()

                # Pandas will auto-create the table if it doesn't exist, which we don't want.
                if not self._table_exists(temp_table_name):
                    raise RuntimeError(f"Table {temp_table_name} does not exist after creation.")

                dataframe.to_sql(
                    temp_table_name,
                    self.get_sql_alchemy_url(),
                    schema=self.config.schema_name,
                    if_exists="append",
                    index=False,
                    dtype=self._get_sql_column_definitions(stream_name),  # type: ignore
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
                    "Deduping was requested but merge-insert is not yet supported.",
                )

            if not self._get_primary_keys(stream_name):
                self._swap_temp_table_with_final_table(
                    stream_name,
                    temp_table_name,
                    final_table_name,
                )
            else:
                self._merge_temp_table_to_final_table(
                    stream_name,
                    temp_table_name,
                    final_table_name,
                )

        else:
            self._append_temp_table_to_final_table(
                stream_name=stream_name,
                temp_table_name=temp_table_name,
                final_table_name=final_table_name,
            )

    def _append_temp_table_to_final_table(
        self,
        temp_table_name: str,
        final_table_name: str,
        stream_name: str,
    ) -> None:
        nl = "\n"
        columns = self._get_sql_column_definitions(stream_name).keys()
        self._execute_sql(
            f"""
            INSERT INTO {self._fully_qualified(final_table_name)} (
            {f',{nl}  '.join(columns)}
            )
            SELECT
            {f',{nl}  '.join(columns)}
            FROM {self._fully_qualified(temp_table_name)}
            """,
        )

    @lru_cache
    def _get_primary_keys(
        self,
        stream_name: str,
    ) -> list[str]:
        pks = self._get_stream_config(stream_name).primary_key
        if not pks:
            return []

        joined_pks = [".".join(pk) for pk in pks]
        for pk in joined_pks:
            if "." in pk:
                msg = "Nested primary keys are not yet supported. Found: {pk}"
                raise NotImplementedError(msg)

        return joined_pks

    def _swap_temp_table_with_final_table(
        self,
        stream_name: str,
        temp_table_name: str,
        final_table_name: str,
    ) -> None:
        """Merge the temp table into the main one.

        This implementation requires MERGE support in the SQL DB.
        Databases that do not support this syntax can override this method.
        """
        if final_table_name is None:
            raise ValueError("Arg 'final_table_name' cannot be None.")
        if temp_table_name is None:
            raise ValueError("Arg 'temp_table_name' cannot be None.")

        _ = stream_name
        deletion_name = f"{final_table_name}_deleteme"
        commands = [
            f"ALTER TABLE {final_table_name} RENAME TO {deletion_name}",
            f"ALTER TABLE {temp_table_name} RENAME TO {final_table_name}",
            f"DROP TABLE {deletion_name}",
        ]
        for cmd in commands:
            self._execute_sql(cmd)

    def _merge_temp_table_to_final_table(
        self,
        stream_name: str,
        temp_table_name: str,
        final_table_name: str,
    ) -> None:
        """Merge the temp table into the main one.

        This implementation requires MERGE support in the SQL DB.
        Databases that do not support this syntax can override this method.
        """
        nl = "\n"
        columns = self._get_sql_column_definitions(stream_name).keys()
        pk_columns = self._get_primary_keys(stream_name)
        non_pk_columns = columns - pk_columns
        join_clause = "{nl} AND ".join(f"tmp.{pk_col} = final.{pk_col}" for pk_col in pk_columns)
        set_clause = "{nl}    ".join(f"{col} = tmp.{col}" for col in non_pk_columns)
        self._execute_sql(
            f"""
            MERGE INTO {self._fully_qualified(final_table_name)} final
            USING (
            SELECT *
            FROM {self._fully_qualified(temp_table_name)}
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
            """,
        )

    @final
    def _table_exists(
        self,
        table_name: str,
    ) -> bool:
        """Return true if the given table exists."""
        return table_name in self._get_tables_list()
