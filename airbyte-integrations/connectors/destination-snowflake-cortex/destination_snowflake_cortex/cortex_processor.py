# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""A Snowflake vector store implementation of the SQL processor."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from textwrap import dedent, indent
from typing import TYPE_CHECKING, cast

import sqlalchemy
from overrides import overrides
from sqlalchemy import text

from airbyte import exceptions as exc
from airbyte._future_cdk.record_processor import RecordProcessorBase
from airbyte._future_cdk.state_writers import StdOutStateWriter
from airbyte._processors.sql.snowflake import (
    SnowflakeConfig,
    SnowflakeSqlProcessor,
    SnowflakeTypeConverter,
)


if TYPE_CHECKING:
    from pathlib import Path

from destination_snowflake_cortex.globals import (
    CHUNK_ID_COLUMN,
    DOCUMENT_CONTENT_COLUMN,
    DOCUMENT_ID_COLUMN,
    EMBEDDING_COLUMN,
    METADATA_COLUMN,
)


@dataclasses.dataclass
class SnowflakeCortexConfig(SnowflakeConfig):
    """A Snowflake configuration for use with Cortex functions."""

    vector_length: int


class SnowflakeCortexTypeConverter(SnowflakeTypeConverter):
    """A class to convert array type into vector."""

    def __init__(
        self,
        conversion_map: dict | None = None,
        *,
        vector_length: int,
    ) -> None:
        self.vector_length = vector_length
        super().__init__(conversion_map)

    @overrides
    def to_sql_type(
        self,
        json_schema_property_def: dict[str, str | dict | list],
    ) -> sqlalchemy.types.TypeEngine:
        """Convert a value to a SQL type."""
        sql_type = super().to_sql_type(json_schema_property_def)
        if isinstance(sql_type, sqlalchemy.types.ARRAY):
            # SQLAlchemy doesn't yet support the `VECTOR` data type.
            # We may want to remove this or update once this resolves:
            # https://github.com/snowflakedb/snowflake-sqlalchemy/issues/499
            return f"VECTOR(FLOAT, {self.vector_length})"

        return sql_type


class SnowflakeCortexSqlProcessor(SnowflakeSqlProcessor):
    """A Snowflake implementation for use with Cortex functions."""

    supports_merge_insert = True
    type_converter_class = SnowflakeCortexTypeConverter
    sql_config: SnowflakeCortexConfig

    def __init__(
        self,
        *,
        catalog_provider: CatalogProvider,
        state_writer: StateWriterBase | None = None,
        sql_config: SnowflakeCortexConfig,
        file_writer: FileWriterBase | None = None,
        temp_dir: Path | None = None,
        temp_file_cleanup: bool = True,
    ) -> None:
        """Custom initialization: Initialize type_converter with vector_length."""
        if not temp_dir and not file_writer:
            raise exc.PyAirbyteInternalError(
                message="Either `temp_dir` or `file_writer` must be provided.",
            )

        state_writer = state_writer or StdOutStateWriter()

        self._sql_config: SnowflakeCortexConfig = sql_config

        # Skip the direct parent's initialization and call the grandparent
        RecordProcessorBase.__init__(
            self,
            state_writer=state_writer,
            catalog_provider=catalog_provider,
        )
        self.file_writer = file_writer or self.file_writer_class(
            cache_dir=cast(Path, temp_dir),
            cleanup=temp_file_cleanup,
        )

        # This is the only line that is different from the base class implementation:
        self.type_converter = self.type_converter_class(vector_length=self.sql_config.vector_length)

        self._cached_table_definitions: dict[str, sqlalchemy.Table] = {}
        self._ensure_schema_exists()

    def _get_column_list_from_table(
        self,
        table_name: str,
    ) -> list[str]:
        """Get column names for passed stream.

        This is overridden due to lack of SQLAlchemy compatibility for the
        `VECTOR` data type.
        """
        conn: Connection = self.sql_config.get_vendor_client()
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE TABLE {table_name};")
        results = cursor.fetchall()
        column_names = [row[0].lower() for row in results]
        cursor.close()
        conn.close()
        return column_names

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

        def path_str(path: Path) -> str:
            return str(path.absolute()).replace("\\", "\\\\")

        put_files_statements = "\n".join([f"PUT 'file://{path_str(file_path)}' {internal_sf_stage_name};" for file_path in files])
        self._execute_sql(put_files_statements)
        columns_list = [self._quote_identifier(c) for c in list(self._get_sql_column_definitions(stream_name).keys())]
        files_list = ", ".join([f"'{f.name}'" for f in files])
        columns_list_str: str = indent("\n, ".join(columns_list), " " * 12)

        # following two lines are different from SnowflakeSqlProcessor
        vector_suffix = f"::Vector(Float, {self.sql_config.vector_length})"
        variant_cols_str: str = ("\n" + " " * 21 + ", ").join(
            [f"$1:{self.normalizer.normalize(col)}{vector_suffix if 'embedding' in col else ''}" for col in columns_list]
        )

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
            FILE_FORMAT = ( TYPE = JSON )
            ;
            """
        )
        self._execute_sql(copy_statement)
        return temp_table_name

    @overrides
    def _add_missing_columns_to_table(
        self,
        stream_name: str,
        table_name: str,
    ) -> None:
        """Use Snowflake Python connector to add new columns to the table"""
        columns = self._get_sql_column_definitions(stream_name)
        existing_columns = self._get_column_list_from_table(table_name)
        for column_name, column_type in columns.items():
            if column_name not in existing_columns:
                self._add_new_column_to_table(table_name, column_name, column_type)
            self._invalidate_table_cache(table_name)
        pass

    def _add_new_column_to_table(
        self,
        table_name: str,
        column_name: str,
        column_type: sqlalchemy.types.TypeEngine,
    ) -> None:
        conn: Connection = self.sql_config.get_vendor_client()
        cursor = conn.cursor()
        cursor.execute(
            text(f"ALTER TABLE {self._fully_qualified(table_name)} " f"ADD COLUMN {column_name} {column_type}"),
        )
        cursor.close()
        conn.close()
