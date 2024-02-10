# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A DuckDB implementation of the cache."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent, indent
from typing import cast

from overrides import overrides

from airbyte_lib._file_writers import ParquetWriter, ParquetWriterConfig
from airbyte_lib.caches.base import SQLCacheBase, SQLCacheConfigBase
from airbyte_lib.telemetry import CacheTelemetryInfo


class DuckDBCacheConfig(SQLCacheConfigBase, ParquetWriterConfig):
    """Configuration for the DuckDB cache.

    Also inherits config from the ParquetWriter, which is responsible for writing files to disk.
    """

    db_path: Path | str
    """Normally db_path is a Path object.

    There are some cases, such as when connecting to MotherDuck, where it could be a string that
    is not also a path, such as "md:" to connect the user's default MotherDuck DB.
    """
    schema_name: str = "main"
    """The name of the schema to write to. Defaults to "main"."""

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        # return f"duckdb:///{self.db_path}?schema={self.schema_name}"
        return f"duckdb:///{self.db_path!s}"

    def get_database_name(self) -> str:
        """Return the name of the database."""
        if self.db_path == ":memory:":
            return "memory"

        # Return the file name without the extension
        return str(self.db_path).split("/")[-1].split(".")[0]


class DuckDBCacheBase(SQLCacheBase):
    """A DuckDB implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.
    """

    config_class = DuckDBCacheConfig
    supports_merge_insert = False

    @overrides
    def get_telemetry_info(self) -> CacheTelemetryInfo:
        return CacheTelemetryInfo("duckdb")

    @overrides
    def _setup(self) -> None:
        """Create the database parent folder if it doesn't yet exist."""
        config = cast(DuckDBCacheConfig, self.config)

        if config.db_path == ":memory:":
            return

        Path(config.db_path).parent.mkdir(parents=True, exist_ok=True)


class DuckDBCache(DuckDBCacheBase):
    """A DuckDB implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    Unlike the Snowflake implementation, we can't use the COPY command to load data
    so we insert as values instead.
    """

    file_writer_class = ParquetWriter

    # TODO: Delete or rewrite this method after DuckDB adds support for primary key inspection.
    # @overrides
    # def _merge_temp_table_to_final_table(
    #     self,
    #     stream_name: str,
    #     temp_table_name: str,
    #     final_table_name: str,
    # ) -> None:
    #     """Merge the temp table into the main one.

    #     This implementation requires MERGE support in the SQL DB.
    #     Databases that do not support this syntax can override this method.
    #     """
    #     if not self._get_primary_keys(stream_name):
    #         raise exc.AirbyteLibInternalError(
    #             message="Primary keys not found. Cannot run merge updates without primary keys.",
    #             context={
    #                 "stream_name": stream_name,
    #             },
    #         )

    #     _ = stream_name
    #     final_table = self._fully_qualified(final_table_name)
    #     staging_table = self._fully_qualified(temp_table_name)
    #     self._execute_sql(
    #         # https://duckdb.org/docs/sql/statements/insert.html
    #         # NOTE: This depends on primary keys being set properly in the final table.
    #         f"""
    #         INSERT OR REPLACE INTO {final_table} BY NAME
    #         (SELECT * FROM {staging_table})
    #         """
    #     )

    @overrides
    def _ensure_compatible_table_schema(
        self,
        stream_name: str,
        *,
        raise_on_error: bool = True,
    ) -> bool:
        """Return true if the given table is compatible with the stream's schema.

        In addition to the base implementation, this also checks primary keys.
        """
        # call super
        if not super()._ensure_compatible_table_schema(
            stream_name=stream_name,
            raise_on_error=raise_on_error,
        ):
            return False

        # TODO: Add validation for primary keys after DuckDB adds support for primary key
        #       inspection: https://github.com/Mause/duckdb_engine/issues/594
        #       This is a problem because DuckDB implicitly joins on primary keys during MERGE.
        # pk_cols = self._get_primary_keys(stream_name)
        # table = self.get_sql_table(table_name)
        # table_pk_cols = table.primary_key.columns.keys()
        # if set(pk_cols) != set(table_pk_cols):
        #     if raise_on_error:
        #         raise exc.AirbyteLibCacheTableValidationError(
        #             violation="Primary keys do not match.",
        #             context={
        #                 "stream_name": stream_name,
        #                 "table_name": table_name,
        #                 "expected": pk_cols,
        #                 "found": table_pk_cols,
        #             },
        #         )
        #     return False

        return True

    def _write_files_to_new_table(
        self,
        files: list[Path],
        stream_name: str,
        batch_id: str,
    ) -> str:
        """Write a file(s) to a new table.

        We use DuckDB's `read_parquet` function to efficiently read the files and insert
        them into the table in a single operation.

        Note: This implementation is fragile in regards to column ordering. However, since
        we are inserting into a temp table we have just created, there should be no
        drift between the table schema and the file schema.
        """
        temp_table_name = self._create_table_for_loading(
            stream_name=stream_name,
            batch_id=batch_id,
        )
        columns_list = [
            self._quote_identifier(c)
            for c in list(self._get_sql_column_definitions(stream_name).keys())
        ]
        columns_list_str = indent("\n, ".join(columns_list), "    ")
        files_list = ", ".join([f"'{f!s}'" for f in files])
        insert_statement = dedent(
            f"""
            INSERT INTO {self.config.schema_name}.{temp_table_name}
            (
                {columns_list_str}
            )
            SELECT
                {columns_list_str}
            FROM read_parquet(
                [{files_list}],
                union_by_name = true
            )
            """
        )
        self._execute_sql(insert_statement)
        return temp_table_name
