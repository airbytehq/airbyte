#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from typing import Any, Mapping, Optional
from unittest.mock import MagicMock

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    Level,
    SyncMode,
    Type,
)
from airbyte_cdk.sources.embedded.base_integration import BaseEmbeddedIntegration
from airbyte_cdk.utils import AirbyteTracedException


class TestIntegration(BaseEmbeddedIntegration):
    def _handle_record(self, record: AirbyteRecordMessage, id: Optional[str]) -> Mapping[str, Any]:
        return {"data": record.data, "id": id}


class EmbeddedIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.source_class = MagicMock()
        self.source = MagicMock()
        self.source_class.return_value = self.source
        self.source.spec.return_value = ConnectorSpecification(
            connectionSpecification={
                "properties": {
                    "test": {
                        "type": "string",
                    }
                }
            }
        )
        self.config = {"test": "abc"}
        self.integration = TestIntegration(self.source, self.config)
        self.stream1 = AirbyteStream(
            name="test",
            source_defined_primary_key=[["test"]],
            json_schema={},
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        )
        self.stream2 = AirbyteStream(name="test2", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
        self.source.discover.return_value = AirbyteCatalog(streams=[self.stream2, self.stream1])

    def test_integration(self):
        self.source.read.return_value = [
            AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="test")),
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test", data={"test": 1}, emitted_at=1)),
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test", data={"test": 2}, emitted_at=2)),
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test", data={"test": 3}, emitted_at=3)),
        ]
        result = list(self.integration._load_data("test", None))
        self.assertEqual(
            result,
            [
                {"data": {"test": 1}, "id": "1"},
                {"data": {"test": 2}, "id": "2"},
                {"data": {"test": 3}, "id": "3"},
            ],
        )
        self.source.discover.assert_called_once_with(self.config)
        self.source.read.assert_called_once_with(
            self.config,
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=self.stream1,
                        sync_mode=SyncMode.incremental,
                        destination_sync_mode=DestinationSyncMode.append,
                        primary_key=[["test"]],
                    )
                ]
            ),
            None,
        )

    def test_failed_check(self):
        self.config = {"test": 123}
        with self.assertRaises(AirbyteTracedException) as error:
            TestIntegration(self.source, self.config)
        assert str(error.exception) == "123 is not of type 'string'"

    def test_state(self):
        state = AirbyteStateMessage(data={})
        self.source.read.return_value = [
            AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="test")),
            AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test", data={"test": 1}, emitted_at=1)),
            AirbyteMessage(type=Type.STATE, state=state),
        ]
        result = list(self.integration._load_data("test", None))
        self.assertEqual(
            result,
            [
                {"data": {"test": 1}, "id": "1"},
            ],
        )
        self.integration.last_state = state

    def test_incremental(self):
        state = AirbyteStateMessage(data={})
        list(self.integration._load_data("test", state))
        self.source.read.assert_called_once_with(
            self.config,
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=self.stream1,
                        sync_mode=SyncMode.incremental,
                        destination_sync_mode=DestinationSyncMode.append,
                        primary_key=[["test"]],
                    )
                ]
            ),
            state,
        )

    def test_incremental_without_state(self):
        list(self.integration._load_data("test"))
        self.source.read.assert_called_once_with(
            self.config,
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=self.stream1,
                        sync_mode=SyncMode.incremental,
                        destination_sync_mode=DestinationSyncMode.append,
                        primary_key=[["test"]],
                    )
                ]
            ),
            None,
        )

    def test_incremental_unsupported(self):
        state = AirbyteStateMessage(data={})
        list(self.integration._load_data("test2", state))
        self.source.read.assert_called_once_with(
            self.config,
            ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=self.stream2,
                        sync_mode=SyncMode.full_refresh,
                        destination_sync_mode=DestinationSyncMode.append,
                    )
                ]
            ),
            state,
        )
