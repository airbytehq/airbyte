import unittest
from unittest.mock import patch, MagicMock
from airbyte_cdk import DestinationSyncMode
from airbyte_cdk.models import ConfiguredAirbyteCatalog, AirbyteMessage, AirbyteRecordMessage, Type, AirbyteStream, ConfiguredAirbyteStream, SyncMode
from destination_ragie.destination import DestinationRagie
from destination_ragie.config import RagieConfig
from airbyte_cdk.models import Status

class TestDestinationRagie(unittest.TestCase):

    def setUp(self):
        self.destination = DestinationRagie()
        self.config = {
            "api_key": "dummy-key",
            "connection_id": "conn-id",
            "ragie_index_name": "index-name",
            "content_field_path": ["data", "content"],
            "id_field_path": ["data", "id"],
            "batch_size": 1000,
            "content_hash_field": None,
            "delete_before_sync": False,
            "partition_scope": "Default/Account-wide",
            "extra_metadata_fields": []
        }

        # Fixing the issue by adding supported_sync_modes
        stream = ConfiguredAirbyteStream(
            stream=AirbyteStream(name="test", 
                                 json_schema={"type": "object"}, 
                                 supported_sync_modes=[SyncMode.full_refresh]),
            destination_sync_mode=DestinationSyncMode.append,  # Add the destination_sync_mode argument
            sync_mode=SyncMode.full_refresh,  # Add the sync_mode argument
        )

        self.catalog = ConfiguredAirbyteCatalog(streams=[stream])

    @patch("destination_ragie.client.RagieClient._request")
    def test_check_connection_success(self, mock_request):
        mock_request.return_value = {"documents": []}
        result = self.destination.check(self.config)
        self.assertEqual(result.status, Status.SUCCEEDED)

    @patch("destination_ragie.client.RagieClient._request")
    def test_check_connection_failure(self, mock_request):
        from requests.exceptions import HTTPError

        mock_request.side_effect = HTTPError("401 Client Error: Unauthorized for url")
        result = self.destination.check(self.config)
        self.assertEqual(result.status, Status.FAILED)
        self.assertIn("401", result.message)

    @patch("destination_ragie.writer.RagieWriter.flush")
    @patch("destination_ragie.writer.RagieWriter.queue_write_operation")
    @patch("destination_ragie.writer.RagieWriter.preload_hashes_if_needed")
    @patch("destination_ragie.writer.RagieWriter.__init__", return_value=None)
    def test_write_success(self, mock_init, mock_preload, mock_queue, mock_flush):
        mock_flush.return_value = None
        mock_queue.return_value = None
        mock_preload.return_value = None

        input_messages = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    stream="test",
                    data={"data": {"content": "hello", "id": "1"}},
                    emitted_at=0
                )
            )
        ]

        # Simulate writer instance
        from destination_ragie.writer import RagieWriter
        writer_instance = MagicMock(spec=RagieWriter)
        writer_instance.flush.return_value = None
        writer_instance.queue_write_operation.return_value = None
        writer_instance.preload_hashes_if_needed.return_value = None

        with patch("destination_ragie.destination.RagieWriter", return_value=writer_instance):
            output = list(self.destination.write(self.config, self.catalog, input_messages))
            self.assertEqual(len(output), 1)
            self.assertEqual(output[0].type, Type.RECORD)
