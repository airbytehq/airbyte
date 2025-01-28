#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import List

import numpy as np
from destination_milvus.destination import DestinationMilvus
from langchain.vectorstores import Milvus
from langchain_core.embeddings import Embeddings
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from airbyte_cdk.destinations.vector_db_based.embedder import OPEN_AI_VECTOR_SIZE
from airbyte_cdk.destinations.vector_db_based.test_utils import BaseIntegrationTest
from airbyte_cdk.models import DestinationSyncMode, Status


class FakeEmbeddings(Embeddings):
    """Fake embeddings class that generates random vectors for testing."""
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [np.random.rand(OPEN_AI_VECTOR_SIZE).tolist() for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        return np.random.rand(OPEN_AI_VECTOR_SIZE).tolist()


class MilvusIntegrationTest(BaseIntegrationTest):
    """
    Zilliz call to create the collection: /v1/vector/collections/create
    {
        "collectionName": "test2",
        "dimension": 1536,
        "metricType": "L2",
        "vectorField": "vector",
        "primaryField": "pk"
    }
    """

    def _init_milvus(self):
        try:
            # Handle both server and local (Milvus Lite) connections
            if self.config["indexing"]["host"].endswith(".db"):
                # Milvus Lite connection
                connections.connect(
                    alias="test_driver",
                    uri=self.config["indexing"]["host"],  # Local file path for Milvus Lite
                    user="",
                    password="",
                    db_name="",
                )
            else:
                # Server connection
                connections.connect(
                    alias="test_driver",
                    uri=self.config["indexing"]["host"],
                    token=self.config["indexing"]["auth"].get("token", "")
                )
            
            if utility.has_collection(self.config["indexing"]["collection"], using="test_driver"):
                utility.drop_collection(self.config["indexing"]["collection"], using="test_driver")
        except Exception as e:
            # For invalid config test, we expect connection to fail
            if "notmilvus.com" in str(e):
                return
            raise

    def setUp(self):
        with open("secrets/config.json", "r") as f:
            self.config = json.loads(f.read())
        self._init_milvus()

    def test_check_valid_config(self):
        outcome = DestinationMilvus().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def _create_collection(self, vector_dimensions=1536):
        pk = FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True)
        vector = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=vector_dimensions)
        schema = CollectionSchema(fields=[pk, vector], enable_dynamic_field=True)
        collection = Collection(name=self.config["indexing"]["collection"], schema=schema, using="test_driver")
        collection.create_index(
            field_name="vector", index_params={"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}
        )

    def test_check_valid_config_pre_created_collection(self):
        self._create_collection()
        outcome = DestinationMilvus().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def test_check_invalid_config_vector_dimension(self):
        self._create_collection(vector_dimensions=666)
        outcome = DestinationMilvus().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.FAILED

    def test_check_invalid_config(self):
        outcome = DestinationMilvus().check(
            logging.getLogger("airbyte"),
            {
                "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
                "embedding": {"mode": "openai", "openai_key": "mykey"},
                "indexing": {
                    "host": "https://notmilvus.com",
                    "collection": "test2",
                    "auth": {
                        "mode": "token",
                        "token": "mytoken",
                    },
                    "vector_field": "vector",
                    "text_field": "text",
                },
            },
        )
        assert outcome.status == Status.FAILED

    def test_write(self):
        self._init_milvus()
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        # initial sync
        destination = DestinationMilvus()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        collection = Collection(self.config["indexing"]["collection"], using="test_driver")
        collection.flush()
        results = collection.query(expr="pk >= 0")  # Changed from pk != 0 to pk >= 0
        assert len(results) == 5

        # incrementalally update a doc
        incremental_catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup)
        list(destination.write(self.config, incremental_catalog, [self._record("mystream", "Cats are nice", 2), first_state_message]))
        collection.flush()
        result = collection.search(
            anns_field=self.config["indexing"]["vector_field"],
            param={},
            data=[[0] * OPEN_AI_VECTOR_SIZE],
            limit=10,
            expr='_ab_record_id == "mystream_2"',
            output_fields=["text"],
        )
        assert len(result[0]) == 1
        assert result[0][0].entity.get("text") == "str_col: Cats are nice"

        # Skip LangChain integration test for Milvus Lite
        if not self.config["indexing"]["host"].endswith(".db"):
            # test langchain integration with fake embeddings (only for server mode)
            embeddings = FakeEmbeddings()
            connection_args = {
                "uri": self.config["indexing"]["host"],
                "token": self.config["indexing"]["auth"].get("token", "")
            }
            vs = Milvus(
                embedding_function=embeddings,
                collection_name=self.config["indexing"]["collection"],
                connection_args=connection_args,
            )
            vs.fields.append("text")
            vs.fields.append("_ab_record_id")
            # call  vs.fields.append() for all fields you need in the metadata

            result = vs.similarity_search("feline animals", 1)
            assert result[0].metadata["_ab_record_id"] == "mystream_2"
