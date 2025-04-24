#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import time

import docker
import weaviate
from destination_weaviate.destination import DestinationWeaviate
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Weaviate
from pytest_docker.plugin import get_docker_ip

from airbyte_cdk.destinations.vector_db_based.embedder import OPEN_AI_VECTOR_SIZE
from airbyte_cdk.destinations.vector_db_based.test_utils import BaseIntegrationTest
from airbyte_cdk.models import DestinationSyncMode, Status


WEAVIATE_CONTAINER_NAME = "weaviate-test-container-will-get-deleted"


class WeaviateIntegrationTest(BaseIntegrationTest):
    def _init_weaviate(self):
        env_vars = {
            "QUERY_DEFAULTS_LIMIT": "25",
            "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED": "true",
            "DEFAULT_VECTORIZER_MODULE": "none",
            "CLUSTER_HOSTNAME": "node1",
            "PERSISTENCE_DATA_PATH": "./data",
        }
        self.docker_client = docker.from_env()
        try:
            self.docker_client.containers.get(WEAVIATE_CONTAINER_NAME).remove(force=True)
        except docker.errors.NotFound:
            pass

        self.docker_client.containers.run(
            "semitechnologies/weaviate:1.21.2",
            detach=True,
            environment=env_vars,
            name=WEAVIATE_CONTAINER_NAME,
            ports={8080: ("0.0.0.0", 8081)},
        )
        time.sleep(0.5)
        docker_ip = get_docker_ip()
        self.config["indexing"]["host"] = f"http://{docker_ip}:8081"

        retries = 10
        while retries > 0:
            try:
                self.client = weaviate.Client(url=self.config["indexing"]["host"])
                break
            except Exception as e:
                logging.info(f"error connecting to weaviate with indexer. Retrying in 1 second. Exception: {e}")
                time.sleep(1)
                retries -= 1

    def setUp(self):
        with open("secrets/config.json", "r") as f:
            self.config = json.loads(f.read())
        self._init_weaviate()

    def tearDown(self) -> None:
        self.docker_client.containers.get(WEAVIATE_CONTAINER_NAME).remove(force=True)

    def test_check_valid_config(self):
        outcome = DestinationWeaviate().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def test_check_invalid_config(self):
        outcome = DestinationWeaviate().check(
            logging.getLogger("airbyte"),
            {**self.config, "indexing": {**self.config["indexing"], "host": "http://localhost:9999"}},
        )
        assert outcome.status == Status.FAILED

    def count_objects(self, class_name: str) -> int:
        result = self.client.query.aggregate(class_name).with_fields("meta { count }").do()
        return result["data"]["Aggregate"][class_name][0]["meta"]["count"]

    def test_write_overwrite(self):
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        destination = DestinationWeaviate()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        assert self.count_objects("Mystream") == 5

        second_record_chunk = [self._record("mystream", f"Dogs are number {i}", i + 1000) for i in range(2)]
        list(destination.write(self.config, catalog, [*second_record_chunk, first_state_message]))
        assert self.count_objects("Mystream") == 2

    def test_write_incremental_dedup(self):
        catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        # initial sync
        destination = DestinationWeaviate()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        assert self.count_objects("Mystream") == 5

        # incrementalally update a doc
        incremental_catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup)
        list(destination.write(self.config, incremental_catalog, [self._record("mystream", "Cats are nice", 2), first_state_message]))
        result = (
            self.client.query.get("Mystream", ["text"])
            .with_near_vector({"vector": [0] * OPEN_AI_VECTOR_SIZE})
            .with_where({"path": ["_ab_record_id"], "operator": "Equal", "valueText": "mystream_2"})
            .do()
        )

        assert len(result["data"]["Get"]["Mystream"]) == 1
        assert self.count_objects("Mystream") == 5
        assert result["data"]["Get"]["Mystream"][0]["text"] == "str_col: Cats are nice"

        # test langchain integration
        embeddings = OpenAIEmbeddings(openai_api_key=self.config["embedding"]["openai_key"])
        vs = Weaviate(
            embedding=embeddings,
            by_text=False,
            client=self.client,
            text_key="text",
            index_name="Mystream",
            attributes=["_ab_record_id"],
        )

        result = vs.similarity_search("feline animals", 1)
        assert result[0].metadata["_ab_record_id"] == "mystream_2"
