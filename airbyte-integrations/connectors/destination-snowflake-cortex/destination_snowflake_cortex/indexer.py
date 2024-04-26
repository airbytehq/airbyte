#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from destination_snowflake_cortex.config import SnowflakeCortexIndexingModel
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog

from airbyte.caches import SnowflakeCache
from airbyte._processors.sql.snowflake import SnowflakeSqlProcessor
from typing import Iterable

from airbyte_cdk.models import (
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
)


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
        self.processor = SnowflakeSqlProcessor(cache=cache)
        self.embedding_dimensions = embedding_dimensions
        self.catalog = configured_catalog


    def _get_airbyte_messsages_from_chunks(
            self, 
            document_chunks, 
        )-> Iterable[AirbyteMessage]:
        # to be implemented 
        airbyte_messages = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            record = chunk.record
            # add new fields to the record
            record.data["metadata"] = chunk.metadata
            record.data["page_content"] = chunk.page_content
            record.data["embedding"] = chunk.embedding
            airbyte_messages.append(record)
        print(airbyte_messages)
        return airbyte_messages

    def _update_catalog(self, namespace, stream):
        # to be implemented 
        pass


    def index(self, document_chunks, namespace, stream):
        # get list of airbyte messages from the document chunks

        # update catalog to include new columns

        # call PyAirbyte SQL processor to process the airbyte messages

        pass

    def delete(self, delete_ids, namespace, stream):
        # to be implemented 
        pass 

    def check(self) -> Optional[str]:
        # check database connection by getting the list of tables in the schema 
        self.processor._get_tables_list()
