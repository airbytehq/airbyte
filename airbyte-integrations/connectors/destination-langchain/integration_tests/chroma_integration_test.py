#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging

import chromadb
from airbyte_cdk.models import DestinationSyncMode, Status
from chromadb.api.types import QueryResult
from destination_langchain.destination import DestinationLangchain
from destination_langchain.embedder import OPEN_AI_VECTOR_SIZE
from integration_tests.base_integration_test import LocalIntegrationTest
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma


class ChromaLocalIntegrationTest(LocalIntegrationTest):
    def setUp(self):
        super().setUp()
        with open("secrets/config.json", "r") as f:
            self.config = json.loads(f.read())
        self.config["indexing"] = {
            "destination_path": self.temp_dir,
            "mode": "chroma_local",
        }
        self.chroma_client = chromadb.PersistentClient(path=self.temp_dir)

    def test_check_valid_config(self):
        outcome = DestinationLangchain().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def test_write(self):
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        # initial sync
        destination = DestinationLangchain()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        assert self.chroma_client.get_collection("langchain").count() == 5

        # incrementalally update a doc
        incremental_catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup)
        list(destination.write(self.config, incremental_catalog, [self._record("mystream", "Cats are nice", 2), first_state_message]))
        chroma_result: QueryResult = self.chroma_client.get_collection("langchain").query(
            query_embeddings=[0] * OPEN_AI_VECTOR_SIZE, n_results=10, where={"_record_id": "2"}, include=["documents"]
        )
        assert len(chroma_result["documents"][0]) == 1
        assert chroma_result["documents"][0] == ["str_col: Cats are nice"]

        # test langchain integration
        embeddings = OpenAIEmbeddings(openai_api_key=self.config["embedding"]["openai_key"])
        vector_store = Chroma(embedding_function=embeddings, persist_directory=self.temp_dir)
        result = vector_store.similarity_search("feline animals", 1)
        assert result[0].metadata["_record_id"] == "2"
