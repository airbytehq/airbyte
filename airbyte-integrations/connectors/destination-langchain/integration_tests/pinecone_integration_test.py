#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from time import sleep

import pinecone
from airbyte_cdk.destinations.vector_db_based.embedder import OPEN_AI_VECTOR_SIZE
from airbyte_cdk.models import DestinationSyncMode, Status
from destination_langchain.destination import DestinationLangchain
from integration_tests.base_integration_test import BaseIntegrationTest
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone


class PineconeIntegrationTest(BaseIntegrationTest):
    def _init_pinecone(self):
        pinecone.init(api_key=self.config["indexing"]["pinecone_key"], environment=self.config["indexing"]["pinecone_environment"])
        self._index = pinecone.Index(self.config["indexing"]["index"])

    def _clean_index(self):
        self._init_pinecone()
        zero_vector = [0.0] * OPEN_AI_VECTOR_SIZE
        query_result = self._index.query(vector=zero_vector, top_k=10_000)
        vector_ids = [doc.id for doc in query_result.matches]
        if len(vector_ids) > 0:
            self._index.delete(ids=vector_ids)

    def setUp(self):
        with open("secrets/config.json", "r") as f:
            self.config = json.loads(f.read())

    def tearDown(self):
        self._clean_index()

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
        self._init_pinecone()
        is_starter_pod = pinecone.describe_index(self.config["indexing"]["index"]).pod_type == "starter"
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        # initial sync
        destination = DestinationLangchain()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        if is_starter_pod:
            # Documents might not be available right away because Pinecone is handling them async
            sleep(20)
        assert self._index.describe_index_stats().total_vector_count == 5

        # incrementalally update a doc
        incremental_catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup)
        list(destination.write(self.config, incremental_catalog, [self._record("mystream", "Cats are nice", 2), first_state_message]))
        if is_starter_pod:
            # Documents might not be available right away because Pinecone is handling them async
            sleep(20)
        result = self._index.query(vector=[0] * OPEN_AI_VECTOR_SIZE, top_k=10, filter={"_record_id": "mystream_2"}, include_metadata=True)
        assert len(result.matches) == 1
        assert result.matches[0].metadata["text"] == "str_col: Cats are nice"

        # test langchain integration
        embeddings = OpenAIEmbeddings(openai_api_key=self.config["embedding"]["openai_key"])
        pinecone.init(api_key=self.config["indexing"]["pinecone_key"], environment=self.config["indexing"]["pinecone_environment"])
        vector_store = Pinecone(self._index, embeddings.embed_query, "text")
        result = vector_store.similarity_search("feline animals", 1)
        assert result[0].metadata["_record_id"] == "mystream_2"
