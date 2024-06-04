# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""A Snowflake vector store implementation of the SQL processor."""

from __future__ import annotations

import uuid
from pathlib import Path
from textwrap import dedent, indent
from typing import TYPE_CHECKING, Any

import dpath
import sqlalchemy
from airbyte._processors.file.jsonl import JsonlWriter
from airbyte.secrets import SecretString
from airbyte.types import SQLTypeConverter
from airbyte_cdk.destinations.vector_db_based import embedder
from airbyte_cdk.destinations.vector_db_based.document_processor import (
    DocumentProcessor as DocumentSplitter,
)
from airbyte_cdk.destinations.vector_db_based.document_processor import (
    ProcessingConfigModel as DocumentSplitterConfig,
)
from airbyte_protocol.models import AirbyteRecordMessage
from overrides import overrides
from pydantic import Field
from snowflake import connector
from snowflake.sqlalchemy import URL, VARIANT
from sqlalchemy.engine import Connection
from typing_extensions import Protocol

from destination_snowflake_cortex.common.catalog.catalog_providers import CatalogProvider
from destination_snowflake_cortex.common.sql.sql_processor import SqlConfig, SqlProcessorBase
from destination_snowflake_cortex.globals import (
    CHUNK_ID_COLUMN,
    DOCUMENT_CONTENT_COLUMN,
    DOCUMENT_ID_COLUMN,
    EMBEDDING_COLUMN,
    METADATA_COLUMN,
)

if TYPE_CHECKING:
    from pathlib import Path


class SnowflakeCortexConfig(SqlConfig):
    """A Snowflake configuration for use with Cortex functions."""

    host: str
    username: str
    password: SecretString
    warehouse: str
    database: str
    role: str
    schema_name: str = Field(default="PUBLIC")

    @property
    def cortex_embedding_model(self) -> str | None:
        """Return the Cortex embedding model name.

        If 'None', then we are loading pre-calculated embeddings.

        TODO: Implement this property or remap.
        """
        return None

    @overrides
    def get_database_name(self) -> str:
        """Return the name of the database."""
        return self.database

    @overrides
    def get_sql_alchemy_url(self) -> SecretString:
        """Return the SQLAlchemy URL to use."""
        return SecretString(
            URL(
                account=self.host,
                user=self.username,
                password=self.password,
                database=self.database,
                warehouse=self.warehouse,
                schema=self.schema_name,
                role=self.role,
            )
        )

    def get_vendor_client(self) -> object:
        """Return the Snowflake connection object."""
        return connector.connect(
            user=self.username,
            password=self.password,
            account=self.host,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema_name,
            role=self.role,
        )


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

    @staticmethod
    def get_json_type() -> sqlalchemy.types.TypeEngine:
        """Get the type to use for nested JSON data."""
        return VARIANT()


class EmbeddingConfig(Protocol):
    """A protocol for embedding configuration.

    This is necessary because embedding configs do not have a shared base class.
    """

    mode: str


class SnowflakeCortexSqlProcessor(SqlProcessorBase):
    """A Snowflake implementation for use with Cortex functions."""

    supports_merge_insert = False
    """We use the emulated merge code path because each primary key has multiple rows (chunks)."""

    sql_config: SnowflakeCortexConfig
    """The configuration for the Snowflake processor, including the vector length."""

    splitter_config: DocumentSplitterConfig
    """The configuration for the document splitter."""

    file_writer_class = JsonlWriter
    type_converter_class: type[SnowflakeTypeConverter] = SnowflakeTypeConverter

    def __init__(
        self,
        sql_config: SnowflakeCortexConfig,
        splitter_config: DocumentSplitterConfig,
        embedder_config: EmbeddingConfig,
        catalog_provider: CatalogProvider,
        temp_dir: Path,
        temp_file_cleanup: bool = True,
    ) -> None:
        """Initialize the Snowflake processor."""
        self.splitter_config = splitter_config
        self.embedder_config = embedder_config
        super().__init__(
            sql_config=sql_config,
            catalog_provider=catalog_provider,
            temp_dir=temp_dir,
            temp_file_cleanup=temp_file_cleanup,
        )

    def _get_sql_column_definitions(
        self,
        stream_name: str,
    ) -> dict[str, sqlalchemy.types.TypeEngine]:
        """Return the column definitions for the given stream.

        Return the static static column definitions for cortex streams.
        """
        _ = stream_name  # unused
        return {
            DOCUMENT_ID_COLUMN: self.type_converter_class.get_string_type(),
            CHUNK_ID_COLUMN: self.type_converter_class.get_string_type(),
            METADATA_COLUMN: self.type_converter_class.get_json_type(),
            DOCUMENT_CONTENT_COLUMN: self.type_converter_class.get_json_type(),
            EMBEDDING_COLUMN: f"VECTOR(FLOAT, {self.embedding_dimensions})",
        }

    @overrides
    def _write_files_to_new_table(
        self,
        files: list[Path],
        stream_name: str,
        batch_id: str,
    ) -> str:
        """Write files to a new table.

        This is the same as PyAirbyte's SnowflakeSqlProcessor implementation, migrated here for
        stability. The main differences lie within `_get_sql_column_definitions()`, whose logic is
        abstracted out of this method.
        """
        temp_table_name = self._create_table_for_loading(
            stream_name=stream_name,
            batch_id=batch_id,
        )
        internal_sf_stage_name = f"@%{temp_table_name}"

        def path_str(path: Path) -> str:
            return str(path.absolute()).replace("\\", "\\\\")

        for file_path in files:
            query = f"PUT 'file://{path_str(file_path)}' {internal_sf_stage_name};"
            self._execute_sql(query)

        columns_list = [
            self._quote_identifier(c)
            for c in list(self._get_sql_column_definitions(stream_name).keys())
        ]
        files_list = ", ".join([f"'{f.name}'" for f in files])
        columns_list_str: str = indent("\n, ".join(columns_list), " " * 12)

        # following block is different from SnowflakeSqlProcessor
        vector_suffix = f"::Vector(Float, {self.embedding_dimensions})"
        variant_cols_str: str = ("\n" + " " * 21 + ", ").join([
            f"$1:{col}{vector_suffix if 'embedding' in col else ''}" for col in columns_list
        ])
        if self.sql_config.cortex_embedding_model:  # Currently always false
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
            FILE_FORMAT = ( TYPE = JSON, COMPRESSION = GZIP )
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
        columns_list: list[str] = list(
            self._get_sql_column_definitions(stream_name=stream_name).keys()
        )

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
                ({", ".join(columns_list)})
            SELECT {", ".join(columns_list)}
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
        document_chunks, id_to_delete = self.splitter.process(record_msg)

        # TODO: Decide if we need to incorporate this into the final implementation:
        _ = id_to_delete

        if not self.sql_config.cortex_embedding_model:
            embeddings = self.embedder.embed_documents(
                # TODO: Check this: Expects a list of documents, not chunks (docs are inconsistent)
                documents=document_chunks,
            )
        for i, chunk in enumerate(document_chunks, start=0):
            new_data: dict[str, Any] = {
                DOCUMENT_ID_COLUMN: self._create_document_id(record_msg),
                CHUNK_ID_COLUMN: str(uuid.uuid4().int),
                METADATA_COLUMN: chunk.metadata,
                DOCUMENT_CONTENT_COLUMN: chunk.page_content,
                EMBEDDING_COLUMN: None,
            }
            if not self.sql_config.cortex_embedding_model:
                new_data[EMBEDDING_COLUMN] = embeddings[i]

        self.file_writer.process_record_message(
            record_msg=AirbyteRecordMessage(
                namespace=record_msg.namespace,
                stream=record_msg.stream,
                data=new_data,
                emitted_at=record_msg.emitted_at,
            ),
            stream_schema={
                "type": "object",
                "properties": {
                    DOCUMENT_ID_COLUMN: {"type": "string"},
                    CHUNK_ID_COLUMN: {"type": "string"},
                    METADATA_COLUMN: {"type": "object"},
                    DOCUMENT_CONTENT_COLUMN: {"type": "string"},
                    EMBEDDING_COLUMN: {
                        "type": "array",
                        "items": {"type": "float"},
                    },
                },
            },
        )

    def _get_table_by_name(
        self,
        table_name: str,
        *,
        force_refresh: bool = False,
        shallow_okay: bool = False,
    ) -> sqlalchemy.Table:
        """Return a table object from a table name.

        Workaround: Until `VECTOR` type is supported by the Snowflake SQLAlchemy dialect, we will
        return a table with fixed columns. This is a temporary solution until the dialect is updated.

        Tracking here: https://github.com/snowflakedb/snowflake-sqlalchemy/issues/499
        """
        _ = force_refresh, shallow_okay  # unused
        table = sqlalchemy.Table(
            table_name,
            sqlalchemy.MetaData(),
        )
        for column_name, column_type in self._get_sql_column_definitions(table_name).items():
            table.append_column(
                sqlalchemy.Column(
                    column_name,
                    column_type,
                    primary_key=column_name in [DOCUMENT_ID_COLUMN, CHUNK_ID_COLUMN],
                )
            )
        return table

    def _add_missing_columns_to_table(
        self,
        stream_name: str,
        table_name: str,
    ) -> None:
        """Add missing columns to the table.

        This is a no-op because metadata scans do not work with the `VECTOR` data type.
        """
        pass

    @property
    def embedder(self) -> embedder.Embedder:
        return embedder.create_from_config(
            embedding_config=self.embedder_config,  # type: ignore [arg-type]  # No common base class
            processing_config=self.splitter_config,
        )

    @property
    def embedding_dimensions(self) -> int:
        """Return the number of dimensions for the embeddings."""
        return self.embedder.embedding_dimensions

    @property
    def splitter(self) -> DocumentSplitter:
        return DocumentSplitter(
            config=self.splitter_config,
            catalog=self.catalog_provider.configured_catalog,
        )

    def _create_document_id(self, record_msg: AirbyteRecordMessage) -> str:
        """Create document id based on the primary key values. Returns a random uuid if no primary key is found"""
        stream_name = record_msg.stream
        primary_key = self._get_record_primary_key(record_msg=record_msg)
        if primary_key is not None:
            return f"Stream_{stream_name}_Key_{primary_key}"
        return str(uuid.uuid4().int)

    def _get_record_primary_key(self, record_msg: AirbyteRecordMessage) -> str | None:
        """Create primary key for the record by appending the primary keys."""
        stream_name = record_msg.stream
        primary_keys = self._get_primary_keys(stream_name)

        if not primary_keys:
            return None

        primary_key = []
        for key in primary_keys:
            try:
                primary_key.append(str(dpath.get(record_msg.data, key)))
            except KeyError:
                primary_key.append("__not_found__")
        # return a stringified version of all primary keys
        stringified_primary_key = "_".join(primary_key)
        return stringified_primary_key
