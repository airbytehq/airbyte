#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Optional
import uuid

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from destination_snowflake_cortex.config import SnowflakeCortexIndexingModel
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog

from airbyte.caches import SnowflakeCache
from typing import Iterable

from airbyte_cdk.models import (
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
)

# extra columns to be added to the Airbyte message
DOCUMENT_ID_COLUMN = "document_id"
CHUNK_ID_COLUMN = "chunk_id"
METADATA_COLUMN = "metadata"
PAGE_CONTENT_COLUMN = "page_content"
EMBEDDING_COLUMN = "embedding"

class SnowflakeCortexIndexer(Indexer):
    config: SnowflakeCortexIndexingModel

    def __init__(self, config: SnowflakeCortexIndexingModel, embedding_dimensions: int, configured_catalog: ConfiguredAirbyteCatalog):
        super().__init__(config)
        self.account = config.account
        self.username = config.username
        self.password = config.password
        self.database = config.database
        self.warehouse = config.warehouse
        self.role = config.role
        cache = SnowflakeCache(account=self.account, username=self.username, password=self.password, database=self.database, warehouse=self.warehouse, role=self.role)
        # self.processor = SnowflakeSqlProcessor(cache=cache)
        self.embedding_dimensions = embedding_dimensions
        self.catalog = configured_catalog


    def _get_airbyte_messsages_from_chunks(
            self, 
            document_chunks, 
        )-> Iterable[AirbyteMessage]:
        """Retrieve airbyte messages from chunks and add embedding data to them."""
        airbyte_messages = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            record = chunk.record
            new_data = {}
            new_data[DOCUMENT_ID_COLUMN] = self._create_document_id(record.data)
            new_data[CHUNK_ID_COLUMN] = str(uuid.uuid4().int)
            new_data[METADATA_COLUMN] = chunk.metadata
            new_data[PAGE_CONTENT_COLUMN] = chunk.page_content
            new_data[EMBEDDING_COLUMN] = chunk.embedding
            record.data = new_data 
            airbyte_messages.append(record)
        return airbyte_messages

    def _get_updated_catalog(self)-> ConfiguredAirbyteCatalog:
        """Add new columns and primary keys to catalog"""
        updated_catalog = self.catalog  
        # update each stream in the catalog
        for stream in updated_catalog.streams:
            stream.stream.json_schema["properties"][DOCUMENT_ID_COLUMN] = {"type": "string"}
            stream.stream.json_schema["properties"][CHUNK_ID_COLUMN] = {"type": "string"}
            stream.stream.json_schema["properties"][PAGE_CONTENT_COLUMN] = {"type": "string"}
            stream.stream.json_schema["properties"][METADATA_COLUMN] = {"type": "object"}
            stream.stream.json_schema["properties"][EMBEDDING_COLUMN] = {"type": "vector_array"}
            # set primary key 
            stream.primary_key = [[DOCUMENT_ID_COLUMN]]
        return updated_catalog
    
    def _get_primary_keys(self, stream:str) -> Optional[str]:
        for stream in self.catalog.streams:
            if stream.stream.name == stream:
                return stream.primary_key
        return None
    
    def _create_document_id(self, record: AirbyteMessage) -> str:
        # TODO: create a primary key based on the primary key of the stream
        return str(uuid.uuid4().int)


    def index(self, document_chunks, namespace, stream):
        # get list of airbyte messages from the document chunks
        airbyte_messages = self._get_airbyte_messsages_from_chunks(document_chunks)

        # update catalog to match all columns in the airbyte messages
        if airbyte_messages is not None and len(airbyte_messages) > 0:
            self._add_columns_to_catalog(airbyte_messages[0])

        # TODO: call PyAirbyte SQL processor to process the airbyte messages

        pass

    def delete(self, delete_ids, namespace, stream):
        # to be implemented 
        pass 

    def check(self) -> Optional[str]:
        # check database connection by getting the list of tables in the schema 
        self.processor._get_tables_list()
