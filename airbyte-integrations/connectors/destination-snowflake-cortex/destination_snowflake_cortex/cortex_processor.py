# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""A Snowflake vector store implementation of the SQL processor."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from textwrap import dedent, indent
from typing import TYPE_CHECKING

from overrides import overrides

from airbyte._processors.sql.snowflake import (
    SnowflakeConfig,
    SnowflakeSqlProcessor,
)
from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    Type,
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

    @property
    def cortex_embedding_model(self) -> str | None:
        """Return the Cortex embedding model name.

        If 'None', then we are loading pre-calculated embeddings.

        TODO: Implement this property or remap.
        """
        return None


class SnowflakeCortexSqlProcessor(SnowflakeSqlProcessor):
    """A Snowflake implementation for use with Cortex functions."""

    # Use the "emulated merge" code path because each primary key has multiple rows (chunks)
    supports_merge_insert = False

    # Custom config type includes the vector_length parameter
    sql_config: SnowflakeCortexConfig

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

        # following block is different from SnowflakeSqlProcessor
        vector_suffix = f"::Vector(Float, {self.sql_config.vector_length})"
        variant_cols_str: str = ("\n" + " " * 21 + ", ").join(
            [f"$1:{self.normalizer.normalize(col)}{vector_suffix if 'embedding' in col else ''}" for col in columns_list]
        )
        if self.sql_config.cortex_embedding_model:
            # WARNING: This is untested and may not work as expected.
            variant_cols_str += f"snowflake.cortex.embed('{self.sql_config.cortex_embedding_model}', $1:{DOCUMENT_CONTENT_COLUMN})"

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

    def _emulated_merge_temp_table_to_final_table(
        self,
        stream_name: str,
        temp_table_name: str,
        final_table_name: str,
    ) -> None:
        """Emulate the merge operation using a series of SQL commands.

        This method varies from the SnowflakeSqlProcessor implementation in that multiple rows will exist for each
        primary key. And we need to remove all rows (chunks) for a given primary key before inserting new ones.

        So instead of using UPDATE and then INSERT, we will DELETE all rows for included primary keys and then call
        the append implementation to insert new rows.
        """
        columns_list: list[str] = list(self._get_sql_column_definitions(stream_name=stream_name).keys())

        delete_statement = dedent(
            f"""
            DELETE FROM {final_table_name}
            WHERE {DOCUMENT_ID_COLUMN} IN (
                SELECT {DOCUMENT_ID_COLUMN}
                FROM {temp_table_name}
            );
            """
        )
        append_statement = dedent(
            f"""
            INSERT INTO {final_table_name}
                ({', '.join(columns_list)})
            SELECT ({', '.join(columns_list)})
            FROM {temp_table_name};
            """
        )

        with self.get_sql_connection() as conn:
            # This is a transactional operation to avoid outages, in case
            # a user queries the data during the operation.
            conn.execute(delete_statement)
            conn.execute(append_statement)

    def process_record_message(
        self,
        record_msg: AirbyteRecordMessage,
        stream_schema: dict,
    ) -> None:
        """Write a record to the cache.

        We override the SQLProcessor implementation in order to handle chunking, embedding, etc.

        This method is called for each record message, before the record is written to local file.
        """

        airbyte_messages = []
        for i, chunk in enumerate(document_chunks):
            chunk = document_chunks[i]
            message = AirbyteMessage(type=Type.RECORD, record=chunk.record)
            new_data = {}
            new_data[DOCUMENT_ID_COLUMN] = self._create_document_id(message)
            new_data[CHUNK_ID_COLUMN] = str(uuid.uuid4().int)
            new_data[METADATA_COLUMN] = chunk.metadata
            new_data[DOCUMENT_CONTENT_COLUMN] = chunk.page_content
            new_data[EMBEDDING_COLUMN] = chunk.embedding

        self.file_writer.process_record_message(
            record_msg,
            stream_schema=stream_schema,
        )
