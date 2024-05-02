#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging

from airbyte_cdk.destinations.vector_db_based.embedder import OPEN_AI_VECTOR_SIZE
from airbyte_cdk.destinations.vector_db_based.test_utils import BaseIntegrationTest
from airbyte_cdk.models import DestinationSyncMode, Status
from destination_snowflake_cortex.indexer import SnowflakeCortexIndexer
from destination_snowflake_cortex.destination import DestinationSnowflakeCortex

class SnowflakeCortexIntegrationTest(BaseIntegrationTest):
    def _init_snowflake_cortex(self):
        #self.snowflake_index = SnowflakeCortexIndexer(self.config["indexing"], 0)
        pass 

    def setUp(self):
        with open("secrets/config.json", "r") as f:
            self.config = json.loads(f.read())
        self._init_snowflake_cortex()

    def tearDown(self):
        self._init_snowflake_cortex()
        #self.snowflake_index(delete_all=True)

    def _test_check_valid_config(self):
        outcome = DestinationSnowflakeCortex().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def _test_check_invalid_config(self):
        outcome = DestinationSnowflakeCortex().check(
            logging.getLogger("airbyte"),
            {
                "processing": {"text_fields": ["str_col"], "chunk_size": 1000, "metadata_fields": ["int_col"]},
                "embedding": {"mode": "openai", "openai_key": "mykey"},
                "indexing": {
                    "account": "myaccount",
                    "username": "myaccount",
                    "password": "xxxxxxxxxxxx",
                    "database": "INTEGRATION_TEST",
                    "warehouse": "INTEGRATION_TEST_WAREHOUSE",
                    "role": "ACCOUNTADMIN"
                },
            },
        )
        assert outcome.status == Status.FAILED

    def test_write(self):
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        # initial sync
        destination = DestinationSnowflakeCortex()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        # todo: check the number of records in table "mystream"
        #assert self.pinecone_index.describe_index_stats().total_vector_count == 5x

        # incrementally update a doc (merge does not work right now for snowflake cortex)
        # incremental_catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup)
        #list(destination.write(self.config, incremental_catalog, [self._record("mystream", "Cats are nice", 2), first_state_message]))
        #result = self.pinecone_index.query(
        #    vector=[0] * OPEN_AI_VECTOR_SIZE, top_k=10, filter={"_ab_record_id": "mystream_2"}, include_metadata=True
        #)
        #assert len(result.matches) == 1
        #assert (
        #    result.matches[0].metadata["text"] == "str_col: Cats are nice"
        #), 'Ensure that "str_col" is included in the "text_fields" array under the "processing" section of /secrets/config.json.'

        # todo: test cortex integration - similarity search
        #embeddings = OpenAIEmbeddings(openai_api_key=self.config["embedding"]["openai_key"])
        #self._init_pinecone()
        #vector_store = Pinecone(self.pinecone_index, embeddings.embed_query, "text")
        #result = vector_store.similarity_search("feline animals", 1)
        #assert result[0].metadata["_ab_record_id"] == "mystream_2"
