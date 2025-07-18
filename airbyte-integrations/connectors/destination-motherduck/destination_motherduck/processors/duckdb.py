# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""A DuckDB implementation of the cache."""

from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Sequence
from urllib.parse import parse_qsl, urlparse

import pyarrow as pa
from duckdb_engine import DuckDBEngineWarning
from overrides import overrides
from pydantic import Field
from sqlalchemy import Executable, TextClause, create_engine, text
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError

from airbyte_cdk import DestinationSyncMode
from airbyte_cdk.sql import exceptions as exc
from airbyte_cdk.sql.constants import AB_EXTRACTED_AT_COLUMN, DEBUG_MODE
from airbyte_cdk.sql.secrets import SecretString
from airbyte_cdk.sql.shared.sql_processor import SqlConfig, SqlProcessorBase, SQLRuntimeError


if TYPE_CHECKING:
    from sqlalchemy.engine import Connection, Engine

BUFFER_TABLE_NAME = "_airbyte_temp_buffer_data"
MOTHERDUCK_SCHEME = "md"

logger = logging.getLogger(__name__)


# @dataclass
class DuckDBConfig(SqlConfig):
    """Configuration for DuckDB."""

    db_path: Path | str = Field()
    """Normally db_path is a Path object.

    The database name will be inferred from the file name. For example, given a `db_path` of
    `/path/to/my/duckdb-file`, the database name is `my_db`.
    """

    schema_name: str = Field(default="main")
    """The name of the schema to write to. Defaults to "main"."""

    @overrides
    def get_sql_alchemy_url(self) -> SecretString:
        """Return the SQLAlchemy URL to use."""
        # Suppress warnings from DuckDB about reflection on indices.
        # https://github.com/Mause/duckdb_engine/issues/905
        warnings.filterwarnings(
            "ignore",
            message="duckdb-engine doesn't yet support reflection on indices",
            category=DuckDBEngineWarning,
        )
        parsed_db_path = urlparse(self.db_path)
        if parsed_db_path.scheme == MOTHERDUCK_SCHEME:
            path = f"{MOTHERDUCK_SCHEME}:{parsed_db_path.path}"
        else:
            path = parsed_db_path.path
        return SecretString(f"duckdb:///{path!s}")

    def get_duckdb_config(self) -> Dict[str, Any]:
        """Get config dictionary to pass to duckdb"""
        return dict(parse_qsl(urlparse(self.db_path).query))

    @overrides
    def get_database_name(self) -> str:
        """Return the name of the database."""
        if self.db_path == ":memory:":
            return "memory"

        # Split the path on the appropriate separator ("/" or "\")
        split_on: Literal["/", "\\"] = "\\" if "\\" in str(self.db_path) else "/"

        # Return the file name without the extension
        return str(self.db_path).split(sep=split_on)[-1].split(".")[0]

    def _is_file_based_db(self) -> bool:
        """Return whether the database is file-based."""
        if isinstance(self.db_path, Path):
            return True

        db_path_str = str(self.db_path)
        return (
            ("/" in db_path_str or "\\" in db_path_str)
            and db_path_str != ":memory:"
            and f"{MOTHERDUCK_SCHEME}:" not in db_path_str
            and "motherduck:" not in db_path_str
        )

    @overrides
    def get_sql_engine(self) -> Engine:
        """
        Return a new SQL engine to use.

        This method is overridden to:
            - ensure that the database parent directory is created if it doesn't exist.
            - pass the DuckDB query parameters (such as motherduck_token) via the config
        """
        if self._is_file_based_db():
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        return create_engine(
            url=self.get_sql_alchemy_url(),
            echo=DEBUG_MODE,
            execution_options={
                "schema_translate_map": {None: self.schema_name},
            },
            future=True,
        )


class DuckDBSqlProcessor(SqlProcessorBase):
    """A DuckDB implementation of the cache.

    Jsonl is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.
    """

    supports_merge_insert = False
    sql_config: DuckDBConfig

    def _execute_sql(self, sql: str | TextClause | Executable) -> Sequence[Any]:
        """Execute the given SQL statement."""
        if isinstance(sql, str):
            sql = text(sql)

        with self.get_sql_connection() as conn:
            try:
                result = conn.execute(sql)
            except (
                ProgrammingError,
                SQLAlchemyError,
            ) as ex:
                msg = f"Error when executing SQL:\n{sql}\n{type(ex).__name__}{ex!s}"
                raise SQLRuntimeError(msg) from None  # from ex

            return result.fetchall()

    def _execute_sql_with_buffer(self, sql: str | TextClause | Executable, buffer_data: pa.Table | None) -> Sequence[Any]:
        """
        Execute the given SQL statement.

        Explicitly register a buffer table to read from.
        """
        if isinstance(sql, str):
            sql = text(sql)

        with self.get_sql_connection() as conn:
            try:
                # This table will now be queryable from DuckDB under the name BUFFER_TABLE_NAME
                conn.execute(text("register(:name, :df)"), {"name": BUFFER_TABLE_NAME, "df": buffer_data})
                result = conn.execute(sql)
            except (
                ProgrammingError,
                SQLAlchemyError,
            ) as ex:
                msg = f"Error when executing SQL:\n{sql}\n{type(ex).__name__}{ex!s}"
                raise SQLRuntimeError(msg) from None  # from ex

            return result.fetchall()

    @overrides
    def _setup(self) -> None:
        """Create the database parent folder if it doesn't yet exist."""
        if self.sql_config.db_path == ":memory:":
            return

        Path(self.sql_config.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _create_table_if_not_exists(
        self,
        table_name: str,
        column_definition_str: str,
        primary_keys: list[str] | None = None,
    ) -> None:
        if primary_keys:
            pk_str = ", ".join(map(self._quote_identifier, primary_keys))
            column_definition_str += f",\n  PRIMARY KEY ({pk_str})"

        cmd = f"""
        CREATE TABLE IF NOT EXISTS {self._fully_qualified(table_name)} (
            {column_definition_str}
        )
        """
        _ = self._execute_sql(cmd)

    def _do_checkpoint(
        self,
        connection: Connection | None = None,
    ) -> None:
        """Checkpoint the given connection.

        We override this method to ensure that the DuckDB WAL is checkpointed explicitly.
        Otherwise DuckDB will lazily flush the WAL to disk, which can cause issues for users
        who want to manipulate the DB files after writing them.

        For more info:
        - https://duckdb.org/docs/sql/statements/checkpoint.html
        """
        if connection is not None:
            connection.execute(text("CHECKPOINT"))
            return

        with self.get_sql_connection() as new_conn:
            new_conn.execute(text("CHECKPOINT"))

    def _executemany(self, sql: str | TextClause | Executable, params: list[list[Any]]) -> None:
        """Execute the given SQL statement."""
        if isinstance(sql, str):
            sql = text(sql)

        with self.get_sql_connection() as conn:
            try:
                entries = list(params)
                conn.engine.pool.connect().executemany(str(sql), entries)  # type: ignore
            except (
                ProgrammingError,
                SQLAlchemyError,
            ) as ex:
                msg = f"Error when executing SQL:\n{sql}\n{type(ex).__name__}{ex!s}"
                raise SQLRuntimeError(msg) from None  # from ex

    def _write_with_executemany(self, buffer: Dict[str, Dict[str, List[Any]]], stream_name: str, table_name: str) -> None:
        column_names_list = list(buffer[stream_name].keys())
        column_names_str = ", ".join(map(self._quote_identifier, column_names_list))
        params = ", ".join(["?"] * len(column_names_list))
        sql = f"""
        -- Write with executemany
        INSERT INTO {self._fully_qualified(table_name)}
            ({column_names_str})
        VALUES ({params})
        """
        entries_to_write = buffer[stream_name]
        num_entries = len(entries_to_write[column_names_list[0]])
        parameters = [[entries_to_write[column_name][n] for column_name in column_names_list] for n in range(num_entries)]
        self._executemany(sql, parameters)

    def _write_from_pa_table(self, table_name: str, stream_name: str, pa_table: pa.Table) -> None:
        full_table_name = self._fully_qualified(table_name)
        columns = list(self._get_sql_column_definitions(stream_name).keys())
        if len(columns) != len(pa_table.column_names):
            warnings.warn(f"Schema has colums: {columns}, buffer has columns: {pa_table.column_names}")
        column_names = ", ".join(map(self._quote_identifier, pa_table.column_names))
        sql = f"""
        -- Write from PyArrow table
        INSERT INTO {full_table_name} ({column_names}) SELECT {column_names} FROM {BUFFER_TABLE_NAME}
        """
        self._execute_sql_with_buffer(sql, buffer_data=pa_table)

    def _write_temp_table_to_target_table(
        self,
        stream_name: str,
        temp_table_name: str,
        final_table_name: str,
        sync_mode: DestinationSyncMode,
    ) -> None:
        """Write the temp table into the final table using the provided write strategy."""
        if sync_mode == DestinationSyncMode.append or sync_mode == DestinationSyncMode.overwrite:
            # Because overwrite drops the table and reinsert all the data
            # we can use the same logic as append.
            # The table is dropped during (_ensure_table_exists)
            self._ensure_compatible_table_schema(
                stream_name=stream_name,
                table_name=final_table_name,
            )
            self._append_temp_table_to_final_table(
                stream_name=stream_name,
                temp_table_name=temp_table_name,
                final_table_name=final_table_name,
            )
            return

        if sync_mode == DestinationSyncMode.append_dedup:
            self._ensure_compatible_table_schema(
                stream_name=stream_name,
                table_name=final_table_name,
            )
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

        raise exc.AirbyteInternalError(
            message="Sync mode is not supported.",
            context={
                "sync_mode": sync_mode,
            },
        )

    def _drop_duplicates(self, table_name: str, stream_name: str) -> str:
        primary_keys = self.catalog_provider.get_primary_keys(stream_name)
        new_table_name = f"{table_name}_deduped"
        if primary_keys:
            pks = ", ".join(primary_keys)
            sql = f"""
            -- Drop duplicates from temp table
            CREATE TABLE {self._fully_qualified(new_table_name)} AS (
                SELECT * FROM {self._fully_qualified(table_name)}
                QUALIFY row_number() OVER (PARTITION BY ({pks}) ORDER BY {AB_EXTRACTED_AT_COLUMN} DESC) = 1
            )
            """
            self._execute_sql(sql)
            return new_table_name
        return table_name

    def _ensure_table_exists(self, stream_name: str, table_name: str, sync_mode: DestinationSyncMode) -> None:
        if sync_mode == DestinationSyncMode.overwrite:
            # delete the tables
            logger.info(f"Dropping tables for overwrite: {table_name}")

            self._drop_temp_table(table_name, if_exists=True)

        # Get the SQL column definitions
        sql_columns = self._get_sql_column_definitions(stream_name)
        column_definition_str = ",\n                ".join(
            f"{self._quote_identifier(column_name)} {sql_type}" for column_name, sql_type in sql_columns.items()
        )

        # create the table if needed
        primary_keys = self.catalog_provider.get_primary_keys(stream_name)
        self._create_table_if_not_exists(
            table_name=table_name,
            column_definition_str=column_definition_str,
            primary_keys=primary_keys,
        )

    def prepare_stream_table(self, stream_name: str, sync_mode: DestinationSyncMode) -> None:
        """
        Ensure schema and table exist, create any missing columns
        """
        self._ensure_schema_exists()
        table_name = self.normalizer.normalize(stream_name)
        self._ensure_table_exists(stream_name=stream_name, table_name=table_name, sync_mode=sync_mode)
        self._ensure_compatible_table_schema(stream_name=stream_name, table_name=table_name)

    def write_stream_data_from_buffer(
        self,
        buffer: Dict[str, Dict[str, List[Any]]],
        stream_name: str,
        sync_mode: DestinationSyncMode,
    ) -> None:
        temp_table_name = self._create_table_for_loading(stream_name, batch_id=None)
        try:
            pa_table = pa.Table.from_pydict(buffer[stream_name])
        except Exception:
            logger.exception(
                "Writing with PyArrow table failed, falling back to writing with executemany. Expect some performance degradation."
            )
            self._write_with_executemany(buffer, stream_name, temp_table_name)
        else:
            # DuckDB will automatically find and SELECT from the `pa_table`
            # local variable defined above.
            self._write_from_pa_table(temp_table_name, stream_name, pa_table)

        temp_table_name_dedup = self._drop_duplicates(temp_table_name, stream_name)

        try:
            self._write_temp_table_to_target_table(
                stream_name=stream_name,
                temp_table_name=temp_table_name_dedup,
                final_table_name=stream_name,
                sync_mode=sync_mode,
            )
        finally:
            self._drop_temp_table(temp_table_name_dedup, if_exists=True)
            self._drop_temp_table(temp_table_name, if_exists=True)
