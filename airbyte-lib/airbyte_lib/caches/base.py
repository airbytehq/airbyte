# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A SQL Cache implementation."""
from __future__ import annotations

import abc
import enum
from contextlib import contextmanager
from functools import cached_property
from typing import TYPE_CHECKING, cast, final

import pandas as pd
import pyarrow as pa
import sqlalchemy
import ulid
from overrides import overrides
from sqlalchemy import (
    Column,
    Table,
    and_,
    create_engine,
    insert,
    null,
    select,
    text,
    update,
)
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.elements import TextClause

from airbyte_lib import exceptions as exc
from airbyte_lib._file_writers.base import FileWriterBase, FileWriterBatchHandle
from airbyte_lib._processors import BatchHandle, RecordProcessor
from airbyte_lib._util.text_util import lower_case_set
from airbyte_lib.caches._catalog_manager import CatalogManager
from airbyte_lib.config import CacheConfigBase
from airbyte_lib.datasets._sql import CachedDataset
from airbyte_lib.strategies import WriteStrategy
from airbyte_lib.types import SQLTypeConverter


if TYPE_CHECKING:
    from collections.abc import Generator, Iterator
    from pathlib import Path

    from sqlalchemy.engine import Connection, Engine
    from sqlalchemy.engine.cursor import CursorResult
    from sqlalchemy.engine.reflection import Inspector
    from sqlalchemy.sql.base import Executable

    from airbyte_protocol.models import (
        AirbyteStateMessage,
        ConfiguredAirbyteCatalog,
    )

    from airbyte_lib.datasets._base import DatasetBase
    from airbyte_lib.telemetry import CacheTelemetryInfo


DEBUG_MODE = False  # Set to True to enable additional debug logging.


class RecordDedupeMode(enum.Enum):
    APPEND = "append"
    REPLACE = "replace"


class SQLRuntimeError(Exception):
    """Raised when an SQL operation fails."""


class SQLCacheConfigBase(CacheConfigBase):
    """Same as a regular config except it exposes the 'get_sql_alchemy_url()' method."""

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
    ) -> None:
        self.config: SQLCacheConfigBase
        self._engine: Engine | None = None
        self._connection_to_reuse: Connection | None = None
        super().__init__(config)
        self._ensure_schema_exists()
        self._catalog_manager = CatalogManager(
            engine=self.get_sql_engine(),
            table_name_resolver=lambda stream_name: self.get_sql_table_name(stream_name),
        )
        self.file_writer = file_writer or self.file_writer_class(
            config, catalog_manager=self._catalog_manager
        )
        self.type_converter = self.type_converter_class()
        self._cached_table_definitions: dict[str, sqlalchemy.Table] = {}

    def __getitem__(self, stream: str) -> DatasetBase:
        return self.streams[stream]

    def __contains__(self, stream: str) -> bool:
        return stream in self._streams_with_data

    def __iter__(self) -> Iterator[str]:
        return iter(self._streams_with_data)

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

        execution_options = {"schema_translate_map": {None: self.config.schema_name}}
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
                execution_options=execution_options,
                # isolation_level="AUTOCOMMIT",
            )
        else:
            # Regular engine creation for new connections
            self._engine = create_engine(
                sql_alchemy_url,
                echo=DEBUG_MODE,
                execution_options=execution_options,
                # isolation_level="AUTOCOMMIT",
            )

        return self._engine

    def _init_connection_settings(self, connection: Connection) -> None:
        """This is called automatically whenever a new connection is created.

        By default this is a no-op. Subclasses can use this to set connection settings, such as
        timezone, case-sensitivity settings, and other session-level variables.
        """
        pass

    @contextmanager
    def get_sql_connection(self) -> Generator[sqlalchemy.engine.Connection, None, None]:
        """A context manager which returns a new SQL connection for running queries.

        If the connection needs to close, it will be closed automatically.
        """
        if self.use_singleton_connection and self._connection_to_reuse is not None:
            connection = self._connection_to_reuse
            self._init_connection_settings(connection)
            yield connection

        else:
            with self.get_sql_engine().begin() as connection:
                self._init_connection_settings(connection)
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
        """Return the main table object for the stream."""
        return self._get_table_by_name(self.get_sql_table_name(stream_name))

    def _get_table_by_name(
        self,
        table_name: str,
        *,
        force_refresh: bool = False,
    ) -> sqlalchemy.Table:
        """Return a table object from a table name.

        To prevent unnecessary round-trips to the database, the table is cached after the first
        query. To ignore the cache and force a refresh, set 'force_refresh' to True.
        """
        if force_refresh or table_name not in self._cached_table_definitions:
            self._cached_table_definitions[table_name] = sqlalchemy.Table(
                table_name,
                sqlalchemy.MetaData(schema=self.config.schema_name),
                autoload_with=self.get_sql_engine(),
            )

        return self._cached_table_definitions[table_name]

    @final
    @property
    def streams(
        self,
    ) -> dict[str, CachedDataset]:
        """Return a temporary table name."""
        result = {}
        for stream_name in self._streams_with_data:
            result[stream_name] = CachedDataset(self, stream_name)

        return result

    # Read methods:

    def get_records(
        self,
        stream_name: str,
    ) -> CachedDataset:
        """Uses SQLAlchemy to select all rows from the table."""
        return CachedDataset(self, stream_name)

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
        except Exception as ex:
            # Ignore schema exists errors.
            if "already exists" not in str(ex):
                raise

        if DEBUG_MODE:
            found_schemas = self._get_schemas_list()
            assert (
                schema_name in found_schemas
            ), f"Schema {schema_name} was not created. Found: {found_schemas}"

    def _quote_identifier(self, identifier: str) -> str:
        """Return the given identifier, quoted."""
        return f'"{identifier}"'

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
        return f"{self.config.schema_name}.{self._quote_identifier(table_name)}"

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
            f"{self._quote_identifier(column_name)} {sql_type}"
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
        *,
        create_if_missing: bool = True,
    ) -> str:
        """Create the final table if it doesn't already exist.

        Return the table name.
        """
        table_name = self.get_sql_table_name(stream_name)
        did_exist = self._table_exists(table_name)
        if not did_exist and create_if_missing:
            column_definition_str = ",\n  ".join(
                f"{self._quote_identifier(column_name)} {sql_type}"
                for column_name, sql_type in self._get_sql_column_definitions(
                    stream_name,
                ).items()
            )
            self._create_table(table_name, column_definition_str)

        return table_name

    def _ensure_compatible_table_schema(
        self,
        stream_name: str,
        *,
        raise_on_error: bool = False,
    ) -> bool:
        """Return true if the given table is compatible with the stream's schema.

        If raise_on_error is true, raise an exception if the table is not compatible.

        TODO: Expand this to check for column types and sizes, and to add missing columns.

        Returns true if the table is compatible, false if it is not.
        """
        json_schema = self._get_stream_json_schema(stream_name)
        stream_column_names: list[str] = json_schema["properties"].keys()
        table_column_names: list[str] = self.get_sql_table(stream_name).columns.keys()

        lower_case_table_column_names = lower_case_set(table_column_names)
        missing_columns = [
            stream_col
            for stream_col in stream_column_names
            if stream_col.lower() not in lower_case_table_column_names
        ]
        if missing_columns:
            if raise_on_error:
                raise exc.AirbyteLibCacheTableValidationError(
                    violation="Cache table is missing expected columns.",
                    context={
                        "stream_column_names": stream_column_names,
                        "table_column_names": table_column_names,
                        "missing_columns": missing_columns,
                    },
                )
            return False  # Some columns are missing.

        return True  # All columns exist.

    @final
    def _create_table(
        self,
        table_name: str,
        column_definition_str: str,
        primary_keys: list[str] | None = None,
    ) -> None:
        if DEBUG_MODE:
            assert table_name not in self._get_tables_list(), f"Table {table_name} already exists."

        if primary_keys:
            pk_str = ", ".join(primary_keys)
            column_definition_str += f",\n  PRIMARY KEY ({pk_str})"

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

    @overrides
    def _write_batch(
        self,
        stream_name: str,
        batch_id: str,
        record_batch: pa.Table,
    ) -> FileWriterBatchHandle:
        """Process a record batch.

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
    def _finalize_batches(
        self,
        stream_name: str,
        write_strategy: WriteStrategy,
    ) -> dict[str, BatchHandle]:
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
                raise_on_error=True,
            )

            temp_table_name = self._write_files_to_new_table(
                files=files,
                stream_name=stream_name,
                batch_id=max_batch_id,
            )
            try:
                self._write_temp_table_to_final_table(
                    stream_name=stream_name,
                    temp_table_name=temp_table_name,
                    final_table_name=final_table_name,
                    write_strategy=write_strategy,
                )
            finally:
                self._drop_temp_table(temp_table_name, if_exists=True)

            # Return the batch handles as measure of work completed.
            return batches_to_finalize

    @overrides
    def _finalize_state_messages(
        self,
        stream_name: str,
        state_messages: list[AirbyteStateMessage],
    ) -> None:
        """Handle state messages by passing them to the catalog manager."""
        if not self._catalog_manager:
            raise exc.AirbyteLibInternalError(
                message="Catalog manager should exist but does not.",
            )
        if state_messages and self._source_name:
            self._catalog_manager.save_state(
                source_name=self._source_name,
                stream_name=stream_name,
                state=state_messages[-1],
            )

    def get_state(self) -> list[dict]:
        """Return the current state of the source."""
        if not self._source_name:
            return []
        if not self._catalog_manager:
            raise exc.AirbyteLibInternalError(
                message="Catalog manager should exist but does not.",
            )
        return (
            self._catalog_manager.get_state(self._source_name, list(self._streams_with_data)) or []
        )

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
        *,
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
                    raise exc.AirbyteLibInternalError(
                        message="Table does not exist after creation.",
                        context={
                            "temp_table_name": temp_table_name,
                        },
                    )

                dataframe.to_sql(
                    temp_table_name,
                    self.get_sql_alchemy_url(),
                    schema=self.config.schema_name,
                    if_exists="append",
                    index=False,
                    dtype=self._get_sql_column_definitions(stream_name),
                )
        return temp_table_name

    @final
    def _write_temp_table_to_final_table(
        self,
        stream_name: str,
        temp_table_name: str,
        final_table_name: str,
        write_strategy: WriteStrategy,
    ) -> None:
        """Write the temp table into the final table using the provided write strategy."""
        has_pks: bool = bool(self._get_primary_keys(stream_name))
        has_incremental_key: bool = bool(self._get_incremental_key(stream_name))
        if write_strategy == WriteStrategy.MERGE and not has_pks:
            raise exc.AirbyteLibInputError(
                message="Cannot use merge strategy on a stream with no primary keys.",
                context={
                    "stream_name": stream_name,
                },
            )

        if write_strategy == WriteStrategy.AUTO:
            if has_pks:
                write_strategy = WriteStrategy.MERGE
            elif has_incremental_key:
                write_strategy = WriteStrategy.APPEND
            else:
                write_strategy = WriteStrategy.REPLACE

        if write_strategy == WriteStrategy.REPLACE:
            self._swap_temp_table_with_final_table(
                stream_name=stream_name,
                temp_table_name=temp_table_name,
                final_table_name=final_table_name,
            )
            return

        if write_strategy == WriteStrategy.APPEND:
            self._append_temp_table_to_final_table(
                stream_name=stream_name,
                temp_table_name=temp_table_name,
                final_table_name=final_table_name,
            )
            return

        if write_strategy == WriteStrategy.MERGE:
            if not self.supports_merge_insert:
                # Fallback to emulated merge if the database does not support merge natively.
                self._emulated_merge_temp_table_to_final_table(
                    stream_name=stream_name,
                    temp_table_name=temp_table_name,
                    final_table_name=final_table_name,
                )
                return

            self._merge_temp_table_to_final_table(
                stream_name=stream_name,
                temp_table_name=temp_table_name,
                final_table_name=final_table_name,
            )
            return

        raise exc.AirbyteLibInternalError(
            message="Write strategy is not supported.",
            context={
                "write_strategy": write_strategy,
            },
        )

    def _append_temp_table_to_final_table(
        self,
        temp_table_name: str,
        final_table_name: str,
        stream_name: str,
    ) -> None:
        nl = "\n"
        columns = [self._quote_identifier(c) for c in self._get_sql_column_definitions(stream_name)]
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

    def _get_incremental_key(
        self,
        stream_name: str,
    ) -> str | None:
        return self._get_stream_config(stream_name).cursor_field

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
            raise exc.AirbyteLibInternalError(message="Arg 'final_table_name' cannot be None.")
        if temp_table_name is None:
            raise exc.AirbyteLibInternalError(message="Arg 'temp_table_name' cannot be None.")

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
        columns = {self._quote_identifier(c) for c in self._get_sql_column_definitions(stream_name)}
        pk_columns = {self._quote_identifier(c) for c in self._get_primary_keys(stream_name)}
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

    def _get_column_by_name(self, table: str | Table, column_name: str) -> Column:
        """Return the column object for the given column name.

        This method is case-insensitive.
        """
        if isinstance(table, str):
            table = self._get_table_by_name(table)
        try:
            # Try to get the column in a case-insensitive manner
            return next(col for col in table.c if col.name.lower() == column_name.lower())
        except StopIteration:
            raise exc.AirbyteLibInternalError(
                message="Could not find matching column.",
                context={
                    "table": table,
                    "column_name": column_name,
                },
            ) from None

    def _emulated_merge_temp_table_to_final_table(
        self,
        stream_name: str,
        temp_table_name: str,
        final_table_name: str,
    ) -> None:
        """Emulate the merge operation using a series of SQL commands.

        This is a fallback implementation for databases that do not support MERGE.
        """
        final_table = self._get_table_by_name(final_table_name)
        temp_table = self._get_table_by_name(temp_table_name)
        pk_columns = self._get_primary_keys(stream_name)

        columns_to_update: set[str] = self._get_sql_column_definitions(
            stream_name=stream_name
        ).keys() - set(pk_columns)

        # Create a dictionary mapping columns in users_final to users_stage for updating
        update_values = {
            self._get_column_by_name(final_table, column): (
                self._get_column_by_name(temp_table, column)
            )
            for column in columns_to_update
        }

        # Craft the WHERE clause for composite primary keys
        join_conditions = [
            self._get_column_by_name(final_table, pk_column)
            == self._get_column_by_name(temp_table, pk_column)
            for pk_column in pk_columns
        ]
        join_clause = and_(*join_conditions)

        # Craft the UPDATE statement
        update_stmt = update(final_table).values(update_values).where(join_clause)

        # Define a join between temp_table and final_table
        joined_table = temp_table.outerjoin(final_table, join_clause)

        # Define a condition that checks for records in temp_table that do not have a corresponding
        # record in final_table
        where_not_exists_clause = self._get_column_by_name(final_table, pk_columns[0]) == null()

        # Select records from temp_table that are not in final_table
        select_new_records_stmt = (
            select([temp_table]).select_from(joined_table).where(where_not_exists_clause)
        )

        # Craft the INSERT statement using the select statement
        insert_new_records_stmt = insert(final_table).from_select(
            names=[column.name for column in temp_table.columns], select=select_new_records_stmt
        )

        if DEBUG_MODE:
            print(str(update_stmt))
            print(str(insert_new_records_stmt))

        with self.get_sql_connection() as conn:
            conn.execute(update_stmt)
            conn.execute(insert_new_records_stmt)

    @final
    def _table_exists(
        self,
        table_name: str,
    ) -> bool:
        """Return true if the given table exists."""
        return table_name in self._get_tables_list()

    @overrides
    def register_source(
        self,
        source_name: str,
        incoming_source_catalog: ConfiguredAirbyteCatalog,
        stream_names: set[str],
    ) -> None:
        """Register the source with the cache.

        We use stream_names to determine which streams will receive data, and
        we only register the stream if is expected to receive data.

        This method is called by the source when it is initialized.
        """
        self._source_name = source_name
        self._ensure_schema_exists()
        super().register_source(
            source_name,
            incoming_source_catalog,
            stream_names=stream_names,
        )

    @property
    @overrides
    def _streams_with_data(self) -> set[str]:
        """Return a list of known streams."""
        if not self._catalog_manager:
            raise exc.AirbyteLibInternalError(
                message="Cannot get streams with data without a catalog.",
            )
        return {
            stream.stream.name
            for stream in self._catalog_manager.source_catalog.streams
            if self._table_exists(self.get_sql_table_name(stream.stream.name))
        }

    @abc.abstractmethod
    def get_telemetry_info(self) -> CacheTelemetryInfo:
        pass
