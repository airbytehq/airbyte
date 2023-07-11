#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging

import pinecone
from airbyte_cdk.models import DestinationSyncMode, Status
from destination_langchain.destination import DestinationLangchain
from destination_langchain.embedder import OPEN_AI_VECTOR_SIZE
from integration_tests.base_integration_test import BaseIntegrationTest
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone


class PineconeIntegrationTest(BaseIntegrationTest):
    def _init_pinecone(self):
        pinecone.init(api_key=self.config["indexing"]["pinecone_key"], environment=self.config["indexing"]["pinecone_environment"])

    def setUp(self):
        with open("secrets/config.json", "r") as f:
            self.config = json.loads(f.read())
        self._init_pinecone()

    def tearDown(self):
        # make sure pinecone is initialized correctly before cleaning up
        self._init_pinecone()
        pinecone.Index("testdata").delete(delete_all=True)

    def test_check_valid_config(self):
        outcome = DestinationLangchain().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def test_check_invalid_config(self):
        outcome = DestinationLangchain().check(
            logging.getLogger("airbyte"),
            {
                "processing": {"text_fields": ["str_col"], "chunk_size": 1000},
                "embedding": {"mode": "openai", "openai_key": "mykey"},
                "indexing": {
                    "mode": "pinecone",
                    "pinecone_key": "mykey",
                    "index": "testdata",
                    "pinecone_environment": "asia-southeast1-gcp-free",
                },
            },
        )
        assert outcome.status == Status.FAILED

    def test_write(self):
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        # initial sync
        destination = DestinationLangchain()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        assert pinecone.Index("testdata").describe_index_stats().total_vector_count == 5

        # incrementalally update a doc
        incremental_catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup)
        list(destination.write(self.config, incremental_catalog, [self._record("mystream", "Cats are nice", 2), first_state_message]))
        result = pinecone.Index("testdata").query(
            vector=[0] * OPEN_AI_VECTOR_SIZE, top_k=10, filter={"_record_id": 2}, include_metadata=True
        )
        assert len(result.matches) == 1
        assert result.matches[0].metadata["text"] == "str_col: Cats are nice"

        # test langchain integration
        embeddings = OpenAIEmbeddings(openai_api_key=self.config["embedding"]["openai_key"])
        pinecone.init(api_key=self.config["indexing"]["pinecone_key"], environment=self.config["indexing"]["pinecone_environment"])
        index = pinecone.Index("testdata")
        vector_store = Pinecone(index, embeddings.embed_query, "text")
        result = vector_store.similarity_search("feline animals", 1)
        assert result[0].metadata["_record_id"] == 2
