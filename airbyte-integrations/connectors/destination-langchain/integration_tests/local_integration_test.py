#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
import tempfile
import time
from typing import Any, Dict, Mapping
import unittest
from destination_langchain.embedder import OPEN_AI_VECTOR_SIZE
from integration_tests.base_integration_test import BaseIntegrationTest

import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)
from destination_langchain.destination import DestinationLangchain
from langchain import OpenAI, PromptTemplate
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import DocArrayHnswSearch
from langchain.embeddings import FakeEmbeddings
import pinecone


class LocalIntegrationTest(BaseIntegrationTest):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "processing": {"text_fields": ["str_col"], "chunk_size": 1000},
            "embedding": {"mode": "fake"},
            "indexing": {"mode": "DocArrayHnswSearch", "destination_path": self.temp_dir},
        }

    def tearDown(self):
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.removedirs(self.temp_dir)

    def test_check_valid_config(self):
        outcome = DestinationLangchain().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def test_check_invalid_config(self):
        os.chmod(self.temp_dir, 0o444)
        outcome = DestinationLangchain().check(
            logging.getLogger("airbyte"),
            self.config
        )
        os.chmod(self.temp_dir, 0o777)
        assert outcome.status == Status.FAILED

    def test_write(self):
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are nice, number {i}", i) for i in range(5)]

        destination = DestinationLangchain()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))

        vector_store = DocArrayHnswSearch.from_params(embedding=FakeEmbeddings(size=OPEN_AI_VECTOR_SIZE), work_dir=self.temp_dir, n_dim=OPEN_AI_VECTOR_SIZE)

        result = vector_store.similarity_search("does not match anyway", 10)
        assert len(result) == 5
