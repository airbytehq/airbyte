#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import unittest
from typing import Any, Dict

from destination_vectara.client import VectaraClient
from destination_vectara.destination import DestinationVectara

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


class VectaraIntegrationTest(unittest.TestCase):
    def _get_configured_catalog(self, destination_mode: DestinationSyncMode) -> ConfiguredAirbyteCatalog:
        stream_schema = {"type": "object", "properties": {"str_col": {"type": "str"}, "int_col": {"type": "integer"}}}

        overwrite_stream = ConfiguredAirbyteStream(
            stream=AirbyteStream(
                name="mystream", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]
            ),
            primary_key=[["int_col"]],
            sync_mode=SyncMode.incremental,
            destination_sync_mode=destination_mode,
        )

        return ConfiguredAirbyteCatalog(streams=[overwrite_stream])

    def _state(self, data: Dict[str, Any]) -> AirbyteMessage:
        return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))

    def _record(self, stream: str, str_value: str, int_value: int) -> AirbyteMessage:
        return AirbyteMessage(
            type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"str_col": str_value, "int_col": int_value}, emitted_at=0)
        )

    def _clean(self):
        self._client.delete_doc_by_metadata(metadata_field_name="_ab_stream", metadata_field_values=["None_mystream"])

    def setUp(self):
        with open("secrets/config.json", "r") as f:
            self.config = json.loads(f.read())
        self._client = VectaraClient(self.config)
        self._clean()

    def tearDown(self):
        self._clean()

    def test_check_valid_config(self):
        outcome = DestinationVectara().check(logging.getLogger("airbyte"), self.config)
        assert outcome.status == Status.SUCCEEDED

    def test_check_invalid_config(self):
        outcome = DestinationVectara().check(
            logging.getLogger("airbyte"),
            {
                "oauth2": {"client_id": "myclientid", "client_secret": "myclientsecret"},
                "corpus_name": "teststore",
                "customer_id": "123456",
                "text_fields": [],
                "metadata_fields": [],
                "title_field": "",
            },
        )
        assert outcome.status == Status.FAILED

    def _query_index(self, query="Everything", num_results=100):
        return self._client._request(
            "query",
            data={
                "query": [
                    {
                        "query": query,
                        "numResults": num_results,
                        "corpusKey": [
                            {
                                "customerId": self._client.customer_id,
                                "corpusId": self._client.corpus_id,
                            }
                        ],
                    }
                ]
            },
        )["responseSet"][0]

    def test_write(self):
        # validate corpus starts empty
        initial_result = self._query_index()["document"]
        assert len(initial_result) == 0

        catalog = self._get_configured_catalog(DestinationSyncMode.overwrite)
        first_state_message = self._state({"state": "1"})
        first_record_chunk = [self._record("mystream", f"Dogs are number {i}", i) for i in range(5)]

        # initial sync
        destination = DestinationVectara()
        list(destination.write(self.config, catalog, [*first_record_chunk, first_state_message]))
        assert len(self._query_index()["document"]) == 5

        # incrementalally update a doc
        incremental_catalog = self._get_configured_catalog(DestinationSyncMode.append_dedup)
        list(destination.write(self.config, incremental_catalog, [self._record("mystream", "Cats are nice", 2), first_state_message]))
        assert len(self._query_index()["document"]) == 5

        # use semantic search
        result = self._query_index("Feline animals", 1)
        assert result["document"] == [
            {
                "id": "Stream_None_mystream_Key_None_mystream_2",
                "metadata": [
                    {"name": "int_col", "value": "2"},
                    {"name": "_ab_stream", "value": "None_mystream"},
                    {"name": "title", "value": "Cats are nice"},
                ],
            }
        ]
