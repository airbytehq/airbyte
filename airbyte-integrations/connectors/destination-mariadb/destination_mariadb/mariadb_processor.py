# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""A MariaDB implementation of the SQL processor."""

from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING, cast, final, Callable
from textwrap import dedent
from typing import Any, Iterable

import dpath
import sqlalchemy
from airbyte._writers import JsonlWriter
from airbyte.shared.state_writers import StateWriterBase, StdOutStateWriter
from pydantic_core import SchemaSerializer, CoreSchema, to_json
from sqlalchemy.engine.reflection import Inspector
from airbyte.strategies import WriteStrategy
from sqlalchemy import text
import logging
logger = logging.getLogger("airbyte")
# from airbyte._processors.file.jsonl import JsonlWriter

# from airbyte.secrets import SecretString
from airbyte.types import SQLTypeConverter
from airbyte_cdk.destinations.vector_db_based.embedder import Document
from airbyte_cdk.models import (
    #AirbyteMessage,
    #AirbyteRecordMessage,
    #AirbyteStateMessage,
    #AirbyteStateType,
    AirbyteStreamState,
    Type,
)
from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
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
    """
    # can I somehow just erase it?
    schema_name: str = Field(default="airbyte_raw")

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

class HackedStdOutStateWriter(StdOutStateWriter):
    def _write_state(
        self,
        state_message: AirbyteStateMessage,
    ) -> None:
        """Save or 'write' a state artifact."""
        # I have no idea why, but model_dump_json doesn't actually exist.
        # Don't believe your IDE, attempting to call it actually causes an exception.
        #print(state_message.model_dump_json())
        logger.info("Attempting to dump a message as JSON")
        print(self.hacked_model_dump_json(state_message))
        logger.info("Seems like we didn't die at least")


    def hacked_model_dump_json(
        self,
        state_message: AirbyteStateMessage,
    ) -> str:
        # needs a "CoreSchema", whatever that is
        # I hope this works. Nope, this doesn't.



        """!!! abstract "Usage Documentation"
            [`model_dump_json`](../concepts/serialization.md#modelmodel_dump_json)

        Generates a JSON representation of the model using Pydantic's `to_json` method.

        Args:
            indent: Indentation to use in the JSON output. If None is passed, the output will be compact.
            include: Field(s) to include in the JSON output.
            exclude: Field(s) to exclude from the JSON output.
            context: Additional context to pass to the serializer.
            by_alias: Whether to serialize using field aliases.
            exclude_unset: Whether to exclude fields that have not been explicitly set.
            exclude_defaults: Whether to exclude fields that are set to their default value.
            exclude_none: Whether to exclude fields that have a value of `None`.
            round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
            warnings: How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors,
                "error" raises a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError].
            fallback: A function to call when an unknown value is encountered. If not provided,
                a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] error is raised.
            serialize_as_any: Whether to serialize fields with duck-typing serialization behavior.

        Returns:
            A JSON string representation of the model.
        """
        return to_json(
            state_message
        ).decode()


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


    _state_writer: StateWriterBase | None

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
        self.temp_tables = {}
        self.splitter_config = splitter_config
        self.embedder_config = embedder_config
        self._state_writer = HackedStdOutStateWriter() # for now
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
            conn.execute(text(statement))

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
            conn.execute(text(delete_statement))
            conn.execute(text(append_statement))

    def _get_placeholder_name(self, identifier: str) -> str:
        return f'{identifier}_val'


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

    def _get_primary_keys(
        self,
        stream_name: str,
    ) -> list[str]:
        pks = self.catalog_provider.get_configured_stream_info(stream_name).primary_key
        if not pks:
            return []

        joined_pks = [".".join(pk) for pk in pks]
        for pk in joined_pks:
            if "." in pk:
                msg = f"Nested primary keys are not yet supported. Found: {pk}"
                raise NotImplementedError(msg)

        return joined_pks

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


    def insert_airbyte_message(
            self,
            stream_name: str,
            table_name: str,
            input_message: AirbyteRecordMessage,
            merge: bool
    ):
        column_defs = self._get_sql_column_definitions(stream_name)
        nl = "\n"
        column_names = []
        column_values = []
        #column_bindprocs = []

        with self.get_sql_connection() as conn:

            dialect = conn.dialect

            for col_name in column_defs:
                col_def = column_defs[col_name]

                column_names.append(self._quote_identifier(col_name))

                # hack. not sure how to do this properly rn. might need proper usage of sqlalchemy.

                if isinstance(col_def, VECTOR):
                    column_values.append('Vec_FromText(:'+self._get_placeholder_name(col_name)+')')
                else:
                    column_values.append(':'+self._get_placeholder_name(col_name))

            query = f"""
                INSERT INTO {self._fully_qualified(table_name)}
                ({f",{nl}  ".join(column_names)})
                VALUES
                ({", ".join(column_values)}) 
            """

            if merge:
                query += f"""{nl} WHERE NOT EXISTS (
                    SELECT {DOCUMENT_ID_COLUMN} 
                    FROM {self._fully_qualified(table_name)}
                    WHERE {DOCUMENT_ID_COLUMN} = {self._get_placeholder_name(DOCUMENT_ID_COLUMN)}
                )"""

            document_chunks, _ = self.splitter.process(input_message)

            embeddings = self.embedder.embed_documents(
                documents=self.chunks_to_documents(document_chunks),
            )



            for i, chunk in enumerate(document_chunks, start=0):

                new_data: dict[str, Any] = {
                    self._get_placeholder_name(DOCUMENT_ID_COLUMN): self._create_document_id(input_message),
                    self._get_placeholder_name(CHUNK_ID_COLUMN): str(uuid.uuid4().int),
                    self._get_placeholder_name(METADATA_COLUMN): json.dumps(chunk.metadata),
                    self._get_placeholder_name(DOCUMENT_CONTENT_COLUMN): chunk.page_content,
                    self._get_placeholder_name(EMBEDDING_COLUMN): embeddings[i],
                }

                for col_name in column_defs:
                    col_def = column_defs[col_name]

                    placeholder_name = self._get_placeholder_name(col_name)

                    bindproc: None | Callable = col_def.bind_processor(dialect)
                    if bindproc is not None:
                        cur_val = new_data[placeholder_name]
                        new_data[placeholder_name] = bindproc(cur_val)

                # I do not know why, but this doesn't seem to do actual binding. Instead, values are escaped and put
                # into the query as strings. This circumvents any "smart" ideas like putting Vec_FromText() into
                # the vector's bind_processor
                conn.execute(text(query), new_data)


    #def encode_

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

    def _ensure_temp_table(self, stream_name):
        """
        Creates a new temp table for the given stream, or returns an existing name
        """
        if stream_name in self.temp_tables:
            return self.temp_tables[stream_name]

        temp_table_name = self._create_table_for_loading(stream_name, None)
        self.temp_tables[stream_name] = temp_table_name
        return temp_table_name

    def _finalize_temp_tables(self):
        for stream_name, temp_table in self.temp_tables:
            final_table_name = self.get_sql_table_name(stream_name)
            self._swap_temp_table_with_final_table(
                stream_name=stream_name,
                temp_table_name=temp_table,
                final_table_name=final_table_name
            )
        pass

    def _get_tables_list(
        self,
    ) -> list[str]:
        """Return a list of all tables in the database."""
        with self.get_sql_connection() as conn:
            inspector: Inspector = sqlalchemy.inspect(conn)
            return inspector.get_table_names()  # type: ignore


    def process_airbyte_record_message(
            self,
            message: AirbyteRecordMessage,
            write_strategy: WriteStrategy,
    ):
        stream_name = message.stream

        self._ensure_final_table_exists(stream_name)
        real_table_name = self.get_sql_table_name(stream_name)

        if write_strategy == WriteStrategy.AUTO:
            write_strategy = self.get_writing_strategy(stream_name)

        if write_strategy == WriteStrategy.REPLACE:
            # - create temp table
            temp_table_name = self._ensure_temp_table(stream_name)

            # - do the processing with appending
            self.insert_airbyte_message(stream_name, temp_table_name, message, False)
            #  _finalize_writing should then swap the tables back
            return


        if write_strategy == WriteStrategy.MERGE:
            # do the processing with merging
            self.insert_airbyte_message(stream_name, real_table_name, message, True)
            return

        if write_strategy == WriteStrategy.APPEND:
            # do the processing with appending
            self.insert_airbyte_message(stream_name, real_table_name, message, False)
            return

    def _finalize_writing(self):
        self._finalize_temp_tables()


    def process_airbyte_messages_as_generator(
            self,
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

        queued_messages = []

        logger.info("Processing message...")
        for message in input_messages:
            # So basically, if it's a record, process it as such. If it's a state, yield it back out

            if message.type is Type.RECORD:
                logger.info("Processing a RECORD")
                self.process_airbyte_record_message(cast(AirbyteRecordMessage, message.record), write_strategy)
                # self.insert_airbyte_message(stream_name, table_name, cast(AirbyteRecordMessage, message), merge)
            elif message.type is Type.STATE:
                logger.info("Processing a STATE")
                # apparently this is necessary for
                # self._state_writer.write_state(message.state)
                # writing shit at the wall and seeing what sticks at this point

                # yielding state messages as-is seems to be correct
                #yield message
                queued_messages.append(message)
            else:
                pass

        # if I yield as I go, instead of queueing them, will this ever be called?
        self._finalize_writing()

        yield from queued_messages
