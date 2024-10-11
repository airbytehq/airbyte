# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""A DuckDB implementation of the cache."""

from __future__ import annotations

import warnings
from pathlib import Path
from textwrap import dedent, indent
from typing import TYPE_CHECKING, Literal

from duckdb_engine import DuckDBEngineWarning
from overrides import overrides
from pydantic import Field
from sqlalchemy import text

from airbyte._writers.jsonl import JsonlWriter
from airbyte.secrets.base import SecretString
from airbyte.shared import SqlProcessorBase
from airbyte.shared.sql_processor import SqlConfig


if TYPE_CHECKING:
    from sqlalchemy.engine import Connection, Engine


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
        return SecretString(f"duckdb:///{self.db_path!s}")

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
            and "md:" not in db_path_str
            and "motherduck:" not in db_path_str
        )

    @overrides
    def get_sql_engine(self) -> Engine:
        """Return the SQL Alchemy engine.

        This method is overridden to ensure that the database parent directory is created if it
        doesn't exist.
        """
        if self._is_file_based_db():
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        return super().get_sql_engine()


class DuckDBSqlProcessor(SqlProcessorBase):
    """A DuckDB implementation of the cache.

    Jsonl is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.
    """

    supports_merge_insert = False
    file_writer_class = JsonlWriter
    sql_config: DuckDBConfig

    @overrides
    def _setup(self) -> None:
        """Create the database parent folder if it doesn't yet exist."""
        if self.sql_config.db_path == ":memory:":
            return

        Path(self.sql_config.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _write_files_to_new_table(
        self,
        files: list[Path],
        stream_name: str,
        batch_id: str,
    ) -> str:
        """Write a file(s) to a new table.

        We use DuckDB native SQL functions to efficiently read the files and insert
        them into the table in a single operation.
        """
        temp_table_name = self._create_table_for_loading(
            stream_name=stream_name,
            batch_id=batch_id,
        )
        columns_list = list(self._get_sql_column_definitions(stream_name=stream_name).keys())
        columns_list_str = indent(
            "\n, ".join([self._quote_identifier(col) for col in columns_list]),
            "    ",
        )
        files_list = ", ".join([f"'{f!s}'" for f in files])
        columns_type_map = indent(
            "\n, ".join(
                [
                    self._quote_identifier(self.normalizer.normalize(prop_name))
                    + ': "'
                    + str(
                        self._get_sql_column_definitions(stream_name)[
                            self.normalizer.normalize(prop_name)
                        ]
                    )
                    + '"'
                    for prop_name in columns_list
                ]
            ),
            "    ",
        )
        insert_statement = dedent(
            f"""
            INSERT INTO {self.sql_config.schema_name}.{temp_table_name}
            (
                {columns_list_str}
            )
            SELECT
                {columns_list_str}
            FROM read_json_auto(
                [{files_list}],
                format = 'newline_delimited',
                union_by_name = true,
                columns = {{ { columns_type_map } }}
            )
            """
        )
        self._execute_sql(insert_statement)
        return temp_table_name

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
