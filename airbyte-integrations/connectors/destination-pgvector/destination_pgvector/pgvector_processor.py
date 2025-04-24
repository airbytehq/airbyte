# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""A PGVector implementation of the SQL processor."""

from __future__ import annotations

import uuid
from pathlib import Path
from textwrap import dedent
from typing import Any

import dpath
import sqlalchemy
from airbyte._processors.file.jsonl import JsonlWriter
from airbyte.secrets import SecretString
from airbyte_cdk.destinations.vector_db_based import embedder
from airbyte_cdk.destinations.vector_db_based.document_processor import (
    DocumentProcessor as DocumentSplitter,
)
from airbyte_cdk.destinations.vector_db_based.document_processor import (
    ProcessingConfigModel as DocumentSplitterConfig,
)
from airbyte_cdk.models import AirbyteRecordMessage
from overrides import overrides
from pgvector.sqlalchemy import Vector
from typing_extensions import Protocol

from destination_pgvector.common.catalog.catalog_providers import CatalogProvider
from destination_pgvector.common.sql.sql_processor import SqlConfig, SqlProcessorBase
from destination_pgvector.globals import (
    CHUNK_ID_COLUMN,
    DOCUMENT_CONTENT_COLUMN,
    DOCUMENT_ID_COLUMN,
    EMBEDDING_COLUMN,
    METADATA_COLUMN,
)


class PostgresConfig(SqlConfig):
    """Configuration for the Postgres cache.

    Also inherits config from the JsonlWriter, which is responsible for writing files to disk.
    """

    host: str
    port: int
    database: str
    username: str
    password: SecretString | str

    @overrides
    def get_sql_alchemy_url(self) -> SecretString:
        """Return the SQLAlchemy URL to use."""
        return SecretString(
            f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        )

    @overrides
    def get_database_name(self) -> str:
        """Return the name of the database."""
        return self.database


class EmbeddingConfig(Protocol):
    """A protocol for embedding configuration.

    This is necessary because embedding configs do not have a shared base class.

    """

    mode: str


class PGVectorProcessor(SqlProcessorBase):
    """A PGVector implementation of the SQL Processor."""

    supports_merge_insert = False
    """We use the emulated merge code path because each primary key has multiple rows (chunks)."""

    sql_config: PostgresConfig
    """The configuration for the PGVector processor, including the vector length."""

    splitter_config: DocumentSplitterConfig
    """The configuration for the document splitter."""

    file_writer_class = JsonlWriter

    # No need to override `type_converter_class`.

    def __init__(
        self,
        sql_config: PostgresConfig,
        splitter_config: DocumentSplitterConfig,
        embedder_config: EmbeddingConfig,
        catalog_provider: CatalogProvider,
        temp_dir: Path,
        temp_file_cleanup: bool = True,
    ) -> None:
        """Initialize the PGVector processor."""
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

        Return the static column definitions for vector index tables.
        """
        _ = stream_name  # unused
        return {
            DOCUMENT_ID_COLUMN: self.type_converter_class.get_string_type(),
            CHUNK_ID_COLUMN: self.type_converter_class.get_string_type(),
            METADATA_COLUMN: self.type_converter_class.get_json_type(),
            DOCUMENT_CONTENT_COLUMN: self.type_converter_class.get_string_type(),
            EMBEDDING_COLUMN: Vector(self.embedding_dimensions),
        }

    def _emulated_merge_temp_table_to_final_table(
        self,
        stream_name: str,
        temp_table_name: str,
        final_table_name: str,
    ) -> None:
        """Emulate the merge operation using a series of SQL commands.

        This method varies from the default SqlProcessor implementation in that multiple rows will exist for each
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
            # This is a transactional operation to avoid "outages", in case
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

        _ = id_to_delete  # unused

        embeddings = self.embedder.embed_documents(
            documents=document_chunks,
        )
        for i, chunk in enumerate(document_chunks, start=0):
            new_data: dict[str, Any] = {
                DOCUMENT_ID_COLUMN: self._create_document_id(record_msg),
                CHUNK_ID_COLUMN: str(uuid.uuid4().int),
                METADATA_COLUMN: chunk.metadata,
                DOCUMENT_CONTENT_COLUMN: chunk.page_content,
                EMBEDDING_COLUMN: embeddings[i],
            }

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
