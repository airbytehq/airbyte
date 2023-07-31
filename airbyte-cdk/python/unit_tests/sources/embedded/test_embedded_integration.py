
from typing import Any, Mapping, Optional
import unittest
from unittest.mock import MagicMock
from airbyte_protocol.models import AirbyteRecordMessage, AirbyteLogMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, SyncMode, DestinationSyncMode
from airbyte_cdk.sources.embedded.base_integration import BaseEmbeddedIntegration

class TestIntegration(BaseEmbeddedIntegration):
    def _handle_record(self, record: AirbyteRecordMessage, id: Optional[str]) -> Mapping[str, Any]:
        return {"data": record.data, "id": id}

class EmbeddedIntegrationTestCase(unittest.TestCase):
    def test_integration(self):
        source_class = MagicMock()
        source = MagicMock()
        source_class.return_value = source
        config = MagicMock()
        integration = TestIntegration(source, config)
        stream1 = MagicMock(name="test", source_defined_primary_key=[["test"]])
        stream2 = MagicMock(name="test2")
        source.discover.return_value = MagicMock(streams=[stream2, stream1])
        source.read.return_value = [
            AirbyteLogMessage(level="info", message="test"),
            AirbyteRecordMessage(stream="test", data={"test": 1}),
            AirbyteRecordMessage(stream="test", data={"test": 2}),
            AirbyteRecordMessage(stream="test", data={"test": 3}),
        ]
        result = [integration._load_data("test", None)]
        self.assertEqual(
            result,
            [
                {"data": {"test": 1}, "id": "1"},
                {"data": {"test": 2}, "id": "2"},
                {"data": {"test": 3}, "id": "3"},
            ],
        )
        source.discover.assert_called_once_with(config)
        source.read.assert_called_once_with(config, ConfiguredAirbyteCatalog(streams=ConfiguredAirbyteStream(stream=stream1, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.append, primary_key=[["test"]])), None)