#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging

from destination_milvus.destination import DestinationMilvus
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Milvus
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from airbyte_cdk.destinations.vector_db_based.embedder import OPEN_AI_VECTOR_SIZE
from airbyte_cdk.destinations.vector_db_based.test_utils import BaseIntegrationTest
from airbyte_cdk.models import DestinationSyncMode, Status


class MilvusIntegrationTest(BaseIntegrationTest):
    """Integration tests for the Milvus destination connector using a local Milvus instance.

    The test suite automatically manages a local Milvus container using the standalone_embed.sh script.
    Tests verify the connector's ability to:
    - Connect to a local Milvus instance
    - Validate configurations
    - Write records in different sync modes
    - Handle vector operations
    """

    def _init_milvus(self):
        """Initialize connection to local Milvus instance."""
        connections.connect(alias="test_driver", host="127.0.0.1", port=19530)
        if utility.has_collection(self.config["indexing"]["collection"], using="test_driver"):
            utility.drop_collection(self.config["indexing"]["collection"], using="test_driver")

    def setUp(self):
        """Set up test resources including local Milvus instance."""
        import subprocess
        from pathlib import Path

        # Start local Milvus using the standalone_embed.sh script
        script_path = Path(__file__).parent / "standalone_embed.sh"
        subprocess.run(["bash", str(script_path), "start"], check=True)

        # Load config for local Milvus instance
        config_path = Path(__file__).parent / "secrets/config.json"
        if not config_path.exists():
            config_path = Path("secrets/config.json")

        with open(config_path, "r") as f:
            self.config = json.loads(f.read())

        # Ensure config points to local instance
        self.config["indexing"]["host"] = "127.0.0.1"
        self.config["indexing"]["port"] = 19530
        if "auth" in self.config["indexing"]:
            del self.config["indexing"]["auth"]
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

    def tearDown(self):
        """Clean up test resources."""
        import subprocess
        from pathlib import Path

        # Stop and cleanup Milvus container
        script_path = Path(__file__).parent / "standalone_embed.sh"
        subprocess.run(["bash", str(script_path), "stop"], check=True)
        subprocess.run(["bash", str(script_path), "delete"], check=True)

    def test_write(self):
        """Test writing records in different sync modes."""
        self._init_milvus()
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        # initial sync
        destination = DestinationMilvus()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        collection = Collection(self.config["indexing"]["collection"], using="test_driver")
        collection.flush()
        assert len(collection.query(expr="pk != 0")) == 5

        # incrementally update a doc
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

        # test langchain integration with local instance
        embeddings = OpenAIEmbeddings(openai_api_key=self.config["embedding"]["openai_key"])
        vs = Milvus(
            embedding_function=embeddings,
            collection_name=self.config["indexing"]["collection"],
            connection_args={"host": "127.0.0.1", "port": 19530},
        )
        vs.fields.append("text")
        vs.fields.append("_ab_record_id")

        result = vs.similarity_search("feline animals", 1)
        assert result[0].metadata["_ab_record_id"] == "mystream_2"
