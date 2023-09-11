#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging

from airbyte_cdk.destinations.vector_db_based.embedder import OPEN_AI_VECTOR_SIZE
from airbyte_cdk.destinations.vector_db_based.test_utils import BaseIntegrationTest
from airbyte_cdk.models import DestinationSyncMode, Status
from destination_milvus.destination import DestinationMilvus
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Milvus
from pymilvus import Collection, connections


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
        connections.connect(alias="test_driver", uri=self.config["indexing"]["host"], token=self.config["indexing"]["auth"]["token"])
        self._collection = Collection(self.config["indexing"]["collection"], using="test_driver")

    def _clean_index(self):
        self._init_milvus()
        entities = self._collection.query(
            expr="pk != 0",
        )
        if len(entities) > 0:
            id_list_expr = ", ".join([str(entity["pk"]) for entity in entities])
            self._collection.delete(expr=f"pk in [{id_list_expr}]")

    def setUp(self):
        with open("secrets/config.json", "r") as f:
            self.config = json.loads(f.read())
        self._clean_index()

    def test_check_valid_config(self):
        outcome = DestinationMilvus().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

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
        self._collection.flush()
        assert len(self._collection.query(expr="pk != 0")) == 5

        # incrementalally update a doc
        incremental_catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup)
        list(destination.write(self.config, incremental_catalog, [self._record("mystream", "Cats are nice", 2), first_state_message]))
        self._collection.flush()
        result = self._collection.search(
            anns_field=self.config["indexing"]["vector_field"],
            param={},
            data=[[0] * OPEN_AI_VECTOR_SIZE],
            limit=10,
            expr='_ab_record_id == "mystream_2"',
            output_fields=["text"],
        )
        assert len(result[0]) == 1
        assert result[0][0].entity.get("text") == "str_col: Cats are nice"

        # test langchain integration
        embeddings = OpenAIEmbeddings(openai_api_key=self.config["embedding"]["openai_key"])
        vs = Milvus(
            embedding_function=embeddings,
            collection_name=self.config["indexing"]["collection"],
            connection_args={"uri": self.config["indexing"]["host"], "token": self.config["indexing"]["auth"]["token"]},
        )
        vs.fields.append("text")
        vs.fields.append("_ab_record_id")
        # call  vs.fields.append() for all fields you need in the metadata

        result = vs.similarity_search("feline animals", 1)
        assert result[0].metadata["_ab_record_id"] == "mystream_2"
