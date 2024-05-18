#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import copy
import uuid
from typing import Any, Iterable, Optional

import dpath.util
from airbyte._processors.sql.snowflake import SnowflakeSqlProcessor
from airbyte._processors.sql.snowflakecortex import SnowflakeCortexSqlProcessor
from airbyte.caches import SnowflakeCache
from airbyte.strategies import WriteStrategy
from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    DestinationSyncMode,
    StreamDescriptor,
    Type,
)
from destination_snowflake_cortex.config import SnowflakeCortexIndexingModel

# extra columns to be added to the Airbyte message
DOCUMENT_ID_COLUMN = "document_id"
CHUNK_ID_COLUMN = "chunk_id"
METADATA_COLUMN = "metadata"
DOCUMENT_CONTENT_COLUMN = "document_content"
EMBEDDING_COLUMN = "embedding"


class SnowflakeCortexIndexer(Indexer):
    config: SnowflakeCortexIndexingModel

    def __init__(self, config: SnowflakeCortexIndexingModel, embedding_dimensions: int, configured_catalog: ConfiguredAirbyteCatalog):
        super().__init__(config)
        self.cache = SnowflakeCache(
            # Note: Host maps to account in the cache
            account=config.host,
            role=config.role,
            warehouse=config.warehouse,
            database=config.database,
            username=config.username,
            password=config.credentials.password,
            schema_name=config.default_schema,
        )
        self.embedding_dimensions = embedding_dimensions
        self.catalog = configured_catalog
        self._init_db_connection()

    def _init_db_connection(self):
        """
        Initialize default snowflake connection for checking the connection. We are not initializing the cortex
        process here because that needs a catalog.
        """
        self.default_processor = SnowflakeSqlProcessor(cache=self.cache)

    def _get_airbyte_messsages_from_chunks(
        self,
        document_chunks: Iterable[Any],
    ) -> Iterable[AirbyteMessage]:
        """Creates Airbyte messages from chunk records."""
        airbyte_messages = []
        for i, chunk in enumerate(document_chunks):
            record_copy = copy.deepcopy(chunk.record)
            message = AirbyteMessage(type=Type.RECORD, record=record_copy)
            new_data = {
                DOCUMENT_ID_COLUMN: self._create_document_id(chunk),
                CHUNK_ID_COLUMN: str(uuid.uuid4().int),
                METADATA_COLUMN: chunk.metadata,
                DOCUMENT_CONTENT_COLUMN: chunk.page_content,
                EMBEDDING_COLUMN: chunk.embedding,
            }
            message.record.data = new_data
            airbyte_messages.append(message)
        return airbyte_messages

    def _get_updated_catalog(self) -> ConfiguredAirbyteCatalog:
        """Adds following columns to catalog
        document_id (primary key) -> unique per record/document
        chunk_id -> unique per chunk
        document_content -> text content of the document
        metadata -> metadata of the record
        embedding -> embedding of the document content
        """
        updated_catalog = copy.deepcopy(self.catalog)
        # update each stream in the catalog
        for stream in updated_catalog.streams:
            # TO-DO: Revisit this - Clear existing properties, if anys, since we are not entirely sure what's in the configured catalog.
            stream.stream.json_schema["properties"] = {}
            stream.stream.json_schema["properties"][DOCUMENT_ID_COLUMN] = {"type": "string"}
            stream.stream.json_schema["properties"][CHUNK_ID_COLUMN] = {"type": "string"}
            stream.stream.json_schema["properties"][DOCUMENT_CONTENT_COLUMN] = {"type": "string"}
            stream.stream.json_schema["properties"][METADATA_COLUMN] = {"type": "object"}
            stream.stream.json_schema["properties"][EMBEDDING_COLUMN] = {"type": "vector_array"}
            # set primary key only if there are existing primary keys
            if stream.primary_key:
                stream.primary_key = [[DOCUMENT_ID_COLUMN]]
        return updated_catalog

    def _get_primary_keys(self, stream_name: str) -> Optional[str]:
        for stream in self.catalog.streams:
            if stream.stream.name == stream_name:
                return stream.primary_key
        return None

    def _get_record_primary_key(self, record: AirbyteMessage) -> Optional[str]:
        """Create primary key for the record by appending the primary keys."""
        stream_name = record.record.stream
        primary_keys = self._get_primary_keys(stream_name)

        if not primary_keys:
            return None

        primary_key = []
        for key in primary_keys:
            try:
                primary_key.append(str(dpath.util.get(record.record.data, key)))
            except KeyError:
                primary_key.append("__not_found__")
        # return a stringified version of all primary keys
        stringified_primary_key = "_".join(primary_key)
        return stringified_primary_key

    def _create_document_id(self, record: AirbyteMessage) -> str:
        """Create document id based on the primary key values. Returns a random uuid if no primary key is found"""
        stream_name = record.record.stream
        primary_key = self._get_record_primary_key(record)
        if primary_key is not None:
            return f"Stream_{stream_name}_Key_{primary_key}"
        return str(uuid.uuid4().int)

    def _create_state_message(self, stream: str, namespace: str, data: dict[str, Any]) -> AirbyteMessage:
        """Create a state message for the stream"""
        stream = AirbyteStreamState(stream_descriptor=StreamDescriptor(name=stream, namespace=namespace))
        return AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(type=AirbyteStateType.STREAM, stream=stream, data=data),
        )

    def get_write_strategy(self, stream_name: str) -> WriteStrategy:
        for stream in self.catalog.streams:
            if stream.stream.name == stream_name:
                if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                    # we will use append here since we will remove the existing records and add new ones.
                    return WriteStrategy.APPEND
                if stream.destination_sync_mode == DestinationSyncMode.append:
                    return WriteStrategy.APPEND
                if stream.destination_sync_mode == DestinationSyncMode.append_dedup:
                    return WriteStrategy.MERGE
        return WriteStrategy.AUTO

    def index(self, document_chunks: Iterable[Any], namespace: str, stream: str):
        # get list of airbyte messages from the document chunks
        airbyte_messages = self._get_airbyte_messsages_from_chunks(document_chunks)
        # todo: remove state messages and see if things still work
        airbyte_messages.append(self._create_state_message(stream, namespace, {}))

        # update catalog to match all columns in the airbyte messages
        if airbyte_messages is not None and len(airbyte_messages) > 0:
            updated_catalog = self._get_updated_catalog()
            cortex_processor = SnowflakeCortexSqlProcessor(
                cache=self.cache,
                catalog=updated_catalog,
                vector_length=self.embedding_dimensions,
                source_name="vector_db_based",
                stream_names=[stream],
            )
            cortex_processor.process_airbyte_messages(airbyte_messages, self.get_write_strategy(stream))

    def delete(self, delete_ids: list[str], namespace: str, stream: str):
        # this delete is specific to vector stores, hence not implemented here
        pass

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        """
        Run before the sync starts. This method makes sure that all records in the destination that belong to streams with a destination mode of overwrite are deleted.
        """
        table_list = self.default_processor._get_tables_list()
        for stream in catalog.streams:
            # remove all records for streams with overwrite mode
            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                stream_name = stream.stream.name
                if stream_name.lower() in [table.lower() for table in table_list]:
                    self.default_processor._execute_sql(f"DELETE FROM {stream_name}")
                pass

    def check(self) -> Optional[str]:
        self.default_processor._get_tables_list()
        # TODO: check to see if vector type is available in snowflake instance
