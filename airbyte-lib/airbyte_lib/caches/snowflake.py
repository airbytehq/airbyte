# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""A Snowflake implementation of the cache."""

from __future__ import annotations

from textwrap import dedent, indent
from typing import TYPE_CHECKING

import sqlalchemy
from overrides import overrides
from snowflake.sqlalchemy import URL, VARIANT

from airbyte_lib._file_writers import ParquetWriter, ParquetWriterConfig
from airbyte_lib.caches.base import (
    RecordDedupeMode,
    SQLCacheBase,
    SQLCacheConfigBase,
)
from airbyte_lib.telemetry import CacheTelemetryInfo
from airbyte_lib.types import SQLTypeConverter


if TYPE_CHECKING:
    from pathlib import Path

    from sqlalchemy.engine import Connection


class SnowflakeCacheConfig(SQLCacheConfigBase, ParquetWriterConfig):
    """Configuration for the Snowflake cache.

    Also inherits config from the ParquetWriter, which is responsible for writing files to disk.
    """

    account: str
    username: str
    password: str
    warehouse: str
    database: str
    role: str

    dedupe_mode = RecordDedupeMode.APPEND

    # Already defined in base class:
    # schema_name: str

    @overrides
    def get_sql_alchemy_url(self) -> str:
        """Return the SQLAlchemy URL to use."""
        return str(
            URL(
                account=self.account,
                user=self.username,
                password=self.password,
                database=self.database,
                warehouse=self.warehouse,
                schema=self.schema_name,
                role=self.role,
            )
        )

    def get_database_name(self) -> str:
        """Return the name of the database."""
        return self.database


class SnowflakeTypeConverter(SQLTypeConverter):
    """A class to convert types for Snowflake."""

    @overrides
    def to_sql_type(
        self,
        json_schema_property_def: dict[str, str | dict | list],
    ) -> sqlalchemy.types.TypeEngine:
        """Convert a value to a SQL type.

        We first call the parent class method to get the type. Then if the type JSON, we
        replace it with VARIANT.
        """
        sql_type = super().to_sql_type(json_schema_property_def)
        if isinstance(sql_type, sqlalchemy.types.JSON):
            return VARIANT()

        return sql_type


class SnowflakeSQLCache(SQLCacheBase):
    """A Snowflake implementation of the cache.

    Parquet is used for local file storage before bulk loading.
    """

    config_class = SnowflakeCacheConfig
    file_writer_class = ParquetWriter
    type_converter_class = SnowflakeTypeConverter

    @overrides
    def _write_files_to_new_table(
        self,
        files: list[Path],
        stream_name: str,
        batch_id: str,
    ) -> str:
        """Write files to a new table."""
        temp_table_name = self._create_table_for_loading(
            stream_name=stream_name,
            batch_id=batch_id,
        )
        internal_sf_stage_name = f"@%{temp_table_name}"
        put_files_statements = "\n".join(
            [
                f"PUT 'file://{file_path.absolute()!s}' {internal_sf_stage_name};"
                for file_path in files
            ]
        )
        self._execute_sql(put_files_statements)

        columns_list = [
            self._quote_identifier(c)
            for c in list(self._get_sql_column_definitions(stream_name).keys())
        ]
        files_list = ", ".join([f"'{f.name}'" for f in files])
        columns_list_str: str = indent("\n, ".join(columns_list), " " * 12)
        variant_cols_str: str = ("\n" + " " * 21 + ", ").join([f"$1:{col}" for col in columns_list])
        copy_statement = dedent(
            f"""
            COPY INTO {temp_table_name}
            (
                {columns_list_str}
            )
            FROM (
                SELECT {variant_cols_str}
                FROM {internal_sf_stage_name}
            )
            FILES = ( {files_list} )
            FILE_FORMAT = ( TYPE = PARQUET )
            ;
            """
        )
        self._execute_sql(copy_statement)
        return temp_table_name

    @overrides
    def _init_connection_settings(self, connection: Connection) -> None:
        """We set Snowflake-specific settings for the session.

        This sets QUOTED_IDENTIFIERS_IGNORE_CASE setting to True, which is necessary because
        Snowflake otherwise will treat quoted table and column references as case-sensitive.
        More info: https://docs.snowflake.com/en/sql-reference/identifiers-syntax

        This also sets MULTI_STATEMENT_COUNT to 0, which allows multi-statement commands.
        """
        connection.execute(
            """
            ALTER SESSION SET
            QUOTED_IDENTIFIERS_IGNORE_CASE = TRUE
            MULTI_STATEMENT_COUNT = 0
            """
        )

    @overrides
    def get_telemetry_info(self) -> CacheTelemetryInfo:
        return CacheTelemetryInfo("snowflake")
