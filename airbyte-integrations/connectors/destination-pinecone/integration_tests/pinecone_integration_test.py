#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
import time

from airbyte_cdk.destinations.vector_db_based.embedder import OPEN_AI_VECTOR_SIZE
from airbyte_cdk.destinations.vector_db_based.test_utils import BaseIntegrationTest
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
from destination_pinecone.destination import DestinationPinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from pinecone import Pinecone as PineconeREST
from pinecone import PineconeException
from pinecone.grpc import PineconeGRPC


class PineconeIntegrationTest(BaseIntegrationTest):
    def _init_pinecone(self):
        self.pc = PineconeGRPC(api_key=self.config["indexing"]["pinecone_key"])
        self.pinecone_index = self.pc.Index(self.config["indexing"]["index"])
        self.pc_rest = PineconeREST(api_key=self.config["indexing"]["pinecone_key"])
        self.pinecone_index_rest = self.pc_rest.Index(name=self.config["indexing"]["index"])
    
    def _wait(self):
        print("Waiting for Pinecone...", end='', flush=True)
        for i in range(15):
            time.sleep(1)
            print(".", end='', flush=True)
        print()  # Move to the next line after the loop
    
    def setUp(self):
        with open("secrets/config.json", "r") as f:
            self.config = json.loads(f.read())
        self._init_pinecone()

    def tearDown(self):
        self._wait()
        # make sure pinecone is initialized correctly before cleaning up        
        self._init_pinecone()
        try:
            self.pinecone_index.delete(delete_all=True)
        except PineconeException as e:
            if "Namespace not found" not in str(e):
                raise(e)
            else :
                print("Nothing to delete in default namespace. No data in the index/namespace.")
        try:
            self.pinecone_index.delete(delete_all=True, namespace="ns1")
        except PineconeException as e:
            if "Namespace not found" not in str(e):
                raise(e)
            else :
                print("Nothing to delete in ns1 namespace. No data in the index/namespace.")

    def test_integration_test_flag_is_set(self):
        assert "PYTEST_CURRENT_TEST" in os.environ

    def test_check_valid_config(self):
        outcome = DestinationPinecone().check(logging.getLogger("airbyte"), self.config)        
        assert outcome.status == Status.SUCCEEDED

    def test_check_invalid_config(self):
        outcome = DestinationPinecone().check(
            logging.getLogger("airbyte"),
            {
                "processing": {"text_fields": ["str_col"], "chunk_size": 1000, "metadata_fields": ["int_col"]},
                "embedding": {"mode": "openai", "openai_key": "mykey"},
                "indexing": {
                    "mode": "pinecone",
                    "pinecone_key": "mykey",
                    "index": "testdata",
                    "pinecone_environment": "us-west1-gcp",
                },
            },
        )
        
        assert outcome.status == Status.FAILED

    def test_write(self):
        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        # initial sync
        destination = DestinationPinecone()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        
    
        self._wait()        
        assert self.pinecone_index.describe_index_stats().total_vector_count == 5

        # incrementalally update a doc
        incremental_catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup)
        list(destination.write(self.config, incremental_catalog, [self._record("mystream", "Cats are nice", 2), first_state_message]))
             
        self._wait() 
        
        result = self.pinecone_index.query(
            vector=[0] * OPEN_AI_VECTOR_SIZE, top_k=10, filter={"_ab_record_id": "mystream_2"}, include_metadata=True
        )
                
        assert len(result.matches) == 1
        assert (
            result.matches[0].metadata["text"] == "str_col: Cats are nice"
        ), 'Ensure that "str_col" is included in the "text_fields" array under the "processing" section of /secrets/config.json.'

        # test langchain integration
        embeddings = OpenAIEmbeddings(openai_api_key=self.config["embedding"]["openai_key"])
        self._init_pinecone()
        vector_store = Pinecone(self.pinecone_index_rest, embeddings.embed_query, "text")
        result = vector_store.similarity_search("feline animals", 1)
        assert result[0].metadata["_ab_record_id"] == "mystream_2"

    def test_write_with_namespace(self):
        catalog = self._get_configured_catalog_with_namespace(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record_with_namespace("mystream", f"Dogs are number {i}", i) for i in range(5)]

        # initial sync
        destination = DestinationPinecone()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))

        self._wait() 
        assert self.pinecone_index.describe_index_stats().total_vector_count == 5


    def _get_configured_catalog_with_namespace(self, destination_mode: DestinationSyncMode) -> ConfiguredAirbyteCatalog:
        stream_schema = {"type": "object", "properties": {"str_col": {"type": "str"}, "int_col": {"type": "integer"}, "random_col": {"type": "integer"}}}

        overwrite_stream = ConfiguredAirbyteStream(
            stream=AirbyteStream(
                name="mystream", 
                namespace="ns1",
                json_schema=stream_schema, 
                supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]
            ),
            primary_key=[["int_col"]],
            sync_mode=SyncMode.incremental,
            destination_sync_mode=destination_mode,
        )

        return ConfiguredAirbyteCatalog(streams=[overwrite_stream])
    
    def _record_with_namespace(self, stream: str, str_value: str, int_value: int) -> AirbyteMessage:
        return AirbyteMessage(
            type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, 
                                                          namespace="ns1",
                                                          data={"str_col": str_value, "int_col": int_value}, 
                                                          emitted_at=0)
        )


    