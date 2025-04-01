# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""A MariaDB implementation of the SQL processor."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING, cast, final
from textwrap import dedent
from typing import Any, Iterable

import dpath
import sqlalchemy
from airbyte._writers import JsonlWriter

from airbyte.strategies import WriteStrategy

# from airbyte._processors.file.jsonl import JsonlWriter

# from airbyte.secrets import SecretString
from airbyte.types import SQLTypeConverter
from airbyte_cdk.destinations.vector_db_based.embedder import Document
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    Type,
)
from airbyte_cdk.destinations.vector_db_based import embedder
from airbyte_cdk.destinations.vector_db_based.document_processor import (
    DocumentProcessor as DocumentSplitter, Chunk,
)
from airbyte_cdk.destinations.vector_db_based.document_processor import (
    ProcessingConfigModel as DocumentSplitterConfig,
)
# from airbyte_cdk.models import AirbyteRecordMessage
from airbyte_cdk.sql.secrets import SecretString
from airbyte_cdk.sql.shared import SqlProcessorBase
from airbyte_cdk.sql.shared.sql_processor import SqlConfig
from airbyte_protocol.models import DestinationSyncMode
from overrides import overrides
from typing_extensions import Protocol

from destination_mariadb.common.catalog.catalog_providers import CatalogProvider
from destination_mariadb.common.sql.mariadb_types import VECTOR
# from destination_mariadb.common.sql.sql_processor import SqlConfig, SqlProcessorBase

from destination_mariadb.globals import (
    CHUNK_ID_COLUMN,
    DOCUMENT_CONTENT_COLUMN,
    DOCUMENT_ID_COLUMN,
    EMBEDDING_COLUMN,
    METADATA_COLUMN,
)

from sqlalchemy.engine import Connection, Engine


class DatabaseConfig(SqlConfig):
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

        # using "mariadb+mariadbconnector" opens a pit to dependency hell, so, not doing that.
        # conn_str = f"mariadb+mariadbconnector://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        conn_str = f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

        return SecretString(
            # this is one of the few places here which is actually DB-specific...
            conn_str
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


class MariaDBProcessor(SqlProcessorBase):
    """A MariaDB implementation of the SQL Processor."""

    supports_merge_insert = True
    """We use the emulated merge code path because each primary key has multiple rows (chunks)."""

    sql_config: DatabaseConfig
    """The configuration for the MariaDB processor, including the vector length."""

    splitter_config: DocumentSplitterConfig
    """The configuration for the document splitter."""

    file_writer_class = JsonlWriter

    sql_engine = None
    """Allow the engine to be overwritten"""

    # No need to override `type_converter_class`.

    def __init__(
            self,
            sql_config: DatabaseConfig,
            splitter_config: DocumentSplitterConfig,
            embedder_config: EmbeddingConfig,
            catalog_provider: CatalogProvider,
            # temp_dir: Path,
            # temp_file_cleanup: bool = True,
    ) -> None:
        """Initialize the MariaDB processor."""
        self.splitter_config = splitter_config
        self.embedder_config = embedder_config
        super().__init__(
            sql_config=sql_config,
            catalog_provider=catalog_provider,
            # temp_dir=temp_dir,
            # temp_file_cleanup=temp_file_cleanup,
        )

    # No, I will override it. Go away with your @final...
    def _get_sql_column_definitions(
            self,
            stream_name: str,
    ) -> dict[str, sqlalchemy.types.TypeEngine]:
        """
        Return the column definitions for the given stream.

        Return the static column definitions for vector index tables.
        """

        _ = stream_name  # unused
        return {
            DOCUMENT_ID_COLUMN: sqlalchemy.types.VARCHAR(length=255),  # self.type_converter_class.get_string_type(), #
            CHUNK_ID_COLUMN: sqlalchemy.types.VARCHAR(length=255),
            METADATA_COLUMN: self.type_converter_class.get_json_type(),
            DOCUMENT_CONTENT_COLUMN: sqlalchemy.types.TEXT(),
            EMBEDDING_COLUMN: VECTOR(self.embedding_dimensions)  # Vector(self.embedding_dimensions),
        }

    def _ensure_schema_exists(self):
        pass

    def _merge_temp_table_to_final_table(
            self,
            stream_name: str,
            temp_table_name: str,
            final_table_name: str,
    ) -> None:
        columns_list: list[str] = list(
            self._get_sql_column_definitions(stream_name=stream_name).keys()
        )

        # for MariaDB, this can probably be replaced by INSERT ... ON DUPLICATE KEY UPDATE
        statement = dedent(
            f"""
            INSERT INTO {final_table_name}
                ({", ".join(columns_list)})
            SELECT {", ".join(columns_list)}
            FROM {temp_table_name}
            ON DUPLICATE KEY UPDATE;
            """
        )

        with self.get_sql_connection() as conn:
            conn.execute(statement)

    def _fully_qualified(
            self,
            table_name: str,
    ) -> str:
        """Return the fully qualified name of the given table."""
        return f"{self._quote_identifier(table_name)}"

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

    def _quote_identifier(self, identifier: str) -> str:
        """Return the given identifier, quoted."""
        return f'`{identifier}`'

    def process_record_message(
            self,
            record_msg: AirbyteRecordMessage,
            stream_schema: dict | None = None,
    ) -> None:
        """Write a record to the cache.

        We override the SQLProcessor implementation in order to handle chunking, embedding, etc.

        This method is called for each record message, before the record is written to local file.
        """
        document_chunks, _ = self.splitter.process(record_msg)

        # _ = id_to_delete  # unused

        # WTF is this even? The docblock says "Embed the text of each CHUNK, so why does it demand Documents?"
        # TODO try to convert chunks to documents, I guess? Basically throw away some of the properties
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

            # self.ins

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

    def process_airbyte_messages(
            self,
            messages: Iterable[AirbyteMessage],
            *,
            write_strategy: WriteStrategy,
    ) -> None:
        # TODO
        """Process a stream of Airbyte messages.
        if not isinstance(write_strategy, WriteStrategy):
            raise exc.AirbyteInternalError(
                message="Invalid `write_strategy` argument. Expected instance of WriteStrategy.",
                context={"write_strategy": write_strategy},
            )
        """

        stream_schemas: dict[str, dict] = {}

        # Process messages, writing to batches as we go
        for message in messages:
            if message.type is Type.RECORD:
                record_msg = cast(AirbyteRecordMessage, message.record)
                stream_name = record_msg.stream

                # TODO is this relevant for me?
                if stream_name not in stream_schemas:
                    stream_schemas[stream_name] = self.catalog_provider.get_stream_json_schema(
                        stream_name=stream_name
                    )

                self.process_record_message(
                    record_msg
                    # stream_schema=stream_schemas[stream_name],
                )

            elif message.type is Type.STATE:
                state_msg = cast(AirbyteStateMessage, message.state)
                if state_msg.type in {AirbyteStateType.GLOBAL, AirbyteStateType.LEGACY}:
                    self._pending_state_messages[f"_{state_msg.type}"].append(state_msg)
                elif state_msg.type is AirbyteStateType.STREAM:
                    stream_state = cast(AirbyteStreamState, state_msg.stream)
                    stream_name = stream_state.stream_descriptor.name
                    self._pending_state_messages[stream_name].append(state_msg)
                else:
                    # TODO
                    """
                    warnings.warn(
                        f"Unexpected state message type. State message was: {state_msg}",
                        stacklevel=2,
                    )
                    """
                    self._pending_state_messages[f"_{state_msg.type}"].append(state_msg)

            else:
                # Ignore unexpected or unhandled message types:
                # Type.LOG, Type.TRACE, Type.CONTROL, etc.
                pass

        # We've finished processing input data.
        # Finalize all received records and state messages:
        self.write_all_stream_data(
            write_strategy=write_strategy,
        )

        # self.cleanup_all()

    def _add_missing_columns_to_table(
            self,
            stream_name: str,
            table_name: str,
    ) -> None:
        """Add missing columns to the table.

        This is a no-op because metadata scans do not work with the `VECTOR` data type.
        ^ that's what it said in PGVector
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

    def get_writing_strategy(
            self,
            stream_name
    ):
        sync_mode = self.catalog_provider.get_configured_stream_info(stream_name).destination_sync_mode

        if sync_mode == DestinationSyncMode.overwrite:
            return WriteStrategy.REPLACE
        elif sync_mode == DestinationSyncMode.append:
            return WriteStrategy.APPEND
        elif sync_mode == DestinationSyncMode.append_dedup:
            return WriteStrategy.MERGE

        return WriteStrategy.APPEND

    def perform_merge_query(self):
        foo = """INSERT INTO foo (field1, field2)
            SELECT 'value1', 'value2'
            FROM DUAL
            WHERE NOT EXISTS (
              SELECT 1
              FROM foo
              WHERE field1='value1'
                AND field2='value2'
            );"""
        pass

    def perform_append_query(
            self,
            stream_name: str,
            table_name: str,
    ):
        nl = "\n"
        columns = [self._quote_identifier(c) for c in self._get_sql_column_definitions(stream_name)]

        # we need to do something

        query = f"""
            INSERT INTO {self._fully_qualified(table_name)}
            {f",{nl}  ".join(columns)}
            VALUES
            ()
        """
        pass

    def insert_airbyte_message(
            self,
            stream_name: str,
            table_name: str,
            input_message: AirbyteRecordMessage,
            merge: bool
    ):
        column_defs = self._get_sql_column_definitions(stream_name)
        nl = "\n"
        columns = [self._quote_identifier(c) for c in column_defs]


        query = f"""
            INSERT INTO {self._fully_qualified(table_name)}
            {f",{nl}  ".join(columns)}
            VALUES
        """

        document_chunks, _ = self.splitter.process(input_message)

        embeddings = self.embedder.embed_documents(
            documents=self.chunks_to_documents(document_chunks),
        )

        insert_lines = []

        for i, chunk in enumerate(document_chunks, start=0):
            # See this: https://stackoverflow.com/questions/76683407/how-to-pass-multiple-parameters-to-insert-into-values-using-sqlalchemy-conne
            for column in column_defs:
                t = column_defs[column]
                t.column_expression()


            new_data: dict[str, Any] = {
                DOCUMENT_ID_COLUMN: self._create_document_id(input_message),
                CHUNK_ID_COLUMN: str(uuid.uuid4().int),
                METADATA_COLUMN: chunk.metadata,
                DOCUMENT_CONTENT_COLUMN: chunk.page_content,
                EMBEDDING_COLUMN: embeddings[i],
            }

            insert_lines.append(f"""
                
            """)

        if merge:
            pass
        else:
            pass
        pass

    def chunks_to_documents(self, chunks: list[Chunk]) -> list[Document]:
        result = []
        for chunk in chunks:
            result.append(Document(
                page_content = chunk.page_content,
                record = chunk.record,
            ))
            pass
        return result

    # foo
    def insert_airbyte_messages(
            self,
            stream_name: str,
            table_name: str,
            input_messages: Iterable[AirbyteMessage],
            merge: bool
    ):

        for message in input_messages:
            # So basically, if it's a record, process it as such. If it's a state, yield it back out

            if message.type is Type.RECORD:
                self.insert_airbyte_message(stream_name, table_name, cast(AirbyteRecordMessage, message), merge)
                pass
            elif message.type is Type.STATE:
                yield cast(AirbyteStateMessage, message)
            else:
                pass

    def process_airbyte_messages_as_generator(
            self,
            stream_name: str,
            input_messages: Iterable[AirbyteMessage],
            write_strategy: WriteStrategy,
    ):
        # ok, so:
        # - for APPEND, we're just going to iterate and append
        # - for MERGE, similar, but do a query which deletes and writes new (or think of something smarter).
        #       see also https://stackoverflow.com/questions/71515981/making-merge-in-mariadb-update-when-matched-insert-when-not-matched
        # - for REPLACE, either empty the table first, or write into a temp table first, then switch them?
        #       probably the latter, because we can have different tables within the same iterable
        # - for AUTO, this is what airbyte says, but pgvector uses the stream's destination_sync_mode
        #     This will use the following logic:
        #       - If there's a primary key, use merge.
        #       - Else, if there's an incremental key, use append.
        #       - Else, use full replace (table swap).

        # sync_mode = self.catalog_provider.get_configured_stream_info(stream_name).destination_sync_mode
        if write_strategy == WriteStrategy.AUTO:
            write_strategy = self.get_writing_strategy(stream_name)

        if write_strategy == WriteStrategy.REPLACE:
            # - create temp table
            temp_table_name = self._create_table_for_loading(stream_name, None)

            # - do the processing with appending
            self.insert_airbyte_messages(stream_name, temp_table_name, input_messages, False)

            # - swap tables
            # - erase other table
            return

        if write_strategy == WriteStrategy.MERGE:
            # do the processing with merging
            return

        if write_strategy == WriteStrategy.APPEND:
            # do the processing with appending
            return

        pass

    def process_airbyte_messages_as_generator_NO(
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
            raise exc.PyAirbyteInputError(
                message="Cannot use merge strategy on a stream with no primary keys.",
                context={
                    "stream_name": stream_name,
                },
            )

        if write_strategy == WriteStrategy.AUTO:
            configured_destination_sync_mode: DestinationSyncMode = (
                self.catalog_provider.get_destination_sync_mode(stream_name)
            )
            if configured_destination_sync_mode == DestinationSyncMode.overwrite:
                write_strategy = WriteStrategy.REPLACE
            elif configured_destination_sync_mode == DestinationSyncMode.append:
                write_strategy = WriteStrategy.APPEND
            elif configured_destination_sync_mode == DestinationSyncMode.append_dedup:
                write_strategy = WriteStrategy.MERGE

            # TODO: Consider removing the rest of these cases if they are dead code.
            elif has_pks:
                write_strategy = WriteStrategy.MERGE
            elif has_incremental_key:
                write_strategy = WriteStrategy.APPEND
            else:
                write_strategy = WriteStrategy.REPLACE

        if write_strategy == WriteStrategy.REPLACE:
            # Note: No need to check for schema compatibility
            # here, because we are fully replacing the table.
            self._swap_temp_table_with_final_table(
                stream_name=stream_name,
                temp_table_name=temp_table_name,
                final_table_name=final_table_name,
            )
            return

        if write_strategy == WriteStrategy.APPEND:
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

        if write_strategy == WriteStrategy.MERGE:
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

        raise exc.PyAirbyteInternalError(
            message="Write strategy is not supported.",
            context={
                "write_strategy": write_strategy,
            },
        )
