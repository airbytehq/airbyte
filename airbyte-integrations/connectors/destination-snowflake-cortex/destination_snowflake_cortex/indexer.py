#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from airbyte_cdk.destinations.vector_db_based.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from destination_snowflake_cortex.config import SnowflakeCortexIndexingModel

from airbyte.caches import SnowflakeCache
from airbyte._processors.sql.snowflake import SnowflakeSqlProcessor


class SnowflakeCortexIndexer(Indexer):
    config: SnowflakeCortexIndexingModel

    def __init__(self, config: SnowflakeCortexIndexingModel, embedding_dimensions: int):
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


    def index(self, document_chunks, namespace, stream):
        # to be implemented 
        pass

    def delete(self, delete_ids, namespace, stream):
        # to be implemented 
        pass 

    def check(self) -> Optional[str]:
        # check database connection by getting the list of tables in the schema 
        self.processor._get_tables_list()
