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
# from airbyte._writers import JsonlWriter
# from airbyte.shared.state_writers import StateWriterBase, StdOutStateWriter
from pydantic_core import SchemaSerializer, CoreSchema, to_json
from sqlalchemy.engine.reflection import Inspector
from airbyte.strategies import WriteStrategy
from sqlalchemy import text
import logging
logger = logging.getLogger("airbyte")
# from airbyte._processors.file.jsonl import JsonlWriter

# from airbyte.secrets import SecretString
from airbyte.secrets import SecretString
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


from airbyte_protocol.models import DestinationSyncMode
from overrides import overrides
from typing_extensions import Protocol

from destination_mariadb.common.catalog.catalog_providers import CatalogProvider
from destination_mariadb.common.sql.mariadb_types import VECTOR
from destination_mariadb.common.sql.sql_processor import SqlConfig, SqlProcessorBase

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


class MariaDBProcessor(SqlProcessorBase):
    """A MariaDB implementation of the SQL Processor."""

    supports_merge_insert = True
    """We use the emulated merge code path because each primary key has multiple rows (chunks)."""

    sql_config: DatabaseConfig
    """The configuration for the MariaDB processor, including the vector length."""

    splitter_config: DocumentSplitterConfig
    """The configuration for the document splitter."""

    # file_writer_class = JsonlWriter

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
        self.temp_tables = {}
        self.splitter_config = splitter_config
        self.embedder_config = embedder_config

        super().__init__(
            sql_config=sql_config,
            catalog_provider=catalog_provider,
            # temp_dir=temp_dir,
            # temp_file_cleanup=temp_file_cleanup,
        )

    # YES
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


    def _fully_qualified(
            self,
            table_name: str,
    ) -> str:
        """Return the fully qualified name of the given table."""
        return f"{self._quote_identifier(table_name)}"


    #yes
    def _get_placeholder_name(self, identifier: str) -> str:
        return f'{identifier}_val'

    # yes
    def _quote_identifier(self, identifier: str) -> str:
        """Return the given identifier, quoted."""
        return f'`{identifier}`'


    def _add_missing_columns_to_table(
            self,
            stream_name: str,
            table_name: str,
    ) -> None:
        """Add missing columns to the table.

        @TODO implement
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

    # yes
    def _create_document_id(self, record_msg: AirbyteRecordMessage) -> str:
        """Create document id based on the primary key values. Returns a random uuid if no primary key is found"""
        stream_name = record_msg.stream
        primary_key = self._get_record_primary_key(record_msg=record_msg)
        if primary_key is not None:
            return f"Stream_{stream_name}_Key_{primary_key}"
        return str(uuid.uuid4().int)

    # yes
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

    # yes
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

    # yes
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


    #yes
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

                # This doesn't seem to do actual binding. Instead, values are escaped and put
                # into the query as strings. This circumvents any "smart" ideas like putting Vec_FromText() into
                # the vector's bind_processor
                conn.execute(text(query), new_data)

    # yes
    def chunks_to_documents(self, chunks: list[Chunk]) -> list[Document]:
        result = []
        for chunk in chunks:
            result.append(Document(
                page_content = chunk.page_content,
                record = chunk.record,
            ))
            pass
        return result

    # yes
    def _ensure_temp_table(self, stream_name):
        """
        Creates a new temp table for the given stream, or returns an existing name
        """
        if stream_name in self.temp_tables:
            return self.temp_tables[stream_name]

        temp_table_name = self._create_table_for_loading(stream_name, None)
        self.temp_tables[stream_name] = temp_table_name
        return temp_table_name

    # yes
    def _finalize_temp_tables(self):
        for stream_name, temp_table in self.temp_tables:
            final_table_name = self.get_sql_table_name(stream_name)
            self._swap_temp_table_with_final_table(
                stream_name=stream_name,
                temp_table_name=temp_table,
                final_table_name=final_table_name
            )
        pass

    # yes
    def _get_tables_list(
        self,
    ) -> list[str]:
        """Return a list of all tables in the database."""
        with self.get_sql_connection() as conn:
            inspector: Inspector = sqlalchemy.inspect(conn)
            return inspector.get_table_names()  # type: ignore


    # YES
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

    # YES
    def _finalize_writing(self):
        self._finalize_temp_tables()


    # YES
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
