# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import unittest
from unittest.mock import MagicMock, Mock, patch

from destination_ragie.config import RagieConfig
from destination_ragie.destination import DestinationRagie

from airbyte_cdk import DestinationSyncMode
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Status,
    SyncMode,
    Type,
)


class TestDestinationRagie(unittest.TestCase):
    def setUp(self):
        self.destination = DestinationRagie()
        self.config = {
            "api_key": "dummy-key",
            "partition": "test_partition",
            "processing_mode": "fast",
            "document_name_field": "id",
            "metadata_fields": ["id"],
            "content_fields": ["content"],
        }

        # Create a test stream
        stream = ConfiguredAirbyteStream(
            stream=AirbyteStream(
                name="test",
                json_schema={
                    "type": "object",
                    "properties": {"data": {"type": "object", "properties": {"content": {"type": "string"}, "id": {"type": "string"}}}},
                },
                supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
            ),
            destination_sync_mode=DestinationSyncMode.append_dedup,
            sync_mode=SyncMode.incremental,
        )

        self.catalog = ConfiguredAirbyteCatalog(streams=[stream])

    @patch("destination_ragie.client.RagieClient._request")
    def test_check_connection_success(self, mock_request):
        """Test that connection check succeeds with valid config."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"documents": []}
        mock_request.return_value = mock_response
        mock_logger = MagicMock()

        result = self.destination.check(config=self.config, logger=mock_logger)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_request.assert_called_once()

    @patch("destination_ragie.client.RagieClient._request")
    def test_check_config_validation_error(self, mock_request):
        """Test that connection check handles config validation errors correctly."""
        # Use an invalid config (missing required fields)
        invalid_config = {}  # Missing other required fields
        mock_logger = MagicMock()

        result = self.destination.check(config=invalid_config, logger=mock_logger)

        self.assertEqual(result.status, Status.FAILED)
        self.assertIn("Configuration validation failed", result.message)
        # Verify the request was never called due to validation error
        mock_request.assert_not_called()

    @patch("destination_ragie.client.RagieClient._request")
    def test_check_unexpected_exception(self, mock_request):
        """Test that connection check handles unexpected exceptions."""
        mock_request.side_effect = Exception("Unexpected error")
        mock_logger = MagicMock()

        result = self.destination.check(config=self.config, logger=mock_logger)

        self.assertEqual(result.status, Status.FAILED)
        self.assertIn("An unexpected error occurred", result.message)

    def test_spec(self):
        """Test that spec returns the correct specification."""
        spec = self.destination.spec()

        self.assertTrue(spec.supportsIncremental)
        self.assertIn(DestinationSyncMode.append, spec.supported_destination_sync_modes)
        self.assertIn(DestinationSyncMode.append_dedup, spec.supported_destination_sync_modes)
        self.assertIn(DestinationSyncMode.overwrite, spec.supported_destination_sync_modes)

    @patch("destination_ragie.destination.RagieWriter")
    def test_write_state_message(self, mock_writer_class):
        """Test that write correctly handles state messages."""
        writer_instance = MagicMock()
        mock_writer_class.return_value = writer_instance

        # Create input with a state message
        state_data = {"bookmarks": {"test_stream": {"cursor": "2021-01-01"}}}
        input_messages = [
            AirbyteMessage(
                type=Type.RECORD, record=AirbyteRecordMessage(stream="test", data={"data": {"content": "hello", "id": "1"}}, emitted_at=0)
            ),
            AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=state_data)),
        ]

        output = list(self.destination.write(self.config, self.catalog, input_messages))

        # Verify the state message was yielded
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0].type, Type.STATE)
        self.assertEqual(output[0].state.data, state_data)

        # Verify record was processed
        writer_instance.queue_write_operation.assert_called_once()

    @patch("destination_ragie.destination.RagieWriter")
    def test_write_error_handling(self, mock_writer_class):
        """Test that write handles errors correctly."""
        writer_instance = MagicMock()
        writer_instance.queue_write_operation.side_effect = Exception("Processing error")
        mock_writer_class.return_value = writer_instance

        input_messages = [
            AirbyteMessage(
                type=Type.RECORD, record=AirbyteRecordMessage(stream="test", data={"data": {"content": "hello", "id": "1"}}, emitted_at=0)
            )
        ]

        with self.assertRaises(Exception):
            list(self.destination.write(self.config, self.catalog, input_messages))

    @patch("destination_ragie.destination.RagieWriter")
    def test_write_delete_streams_to_overwrite(self, mock_writer_class):
        """Test that write calls delete_streams_to_overwrite before processing records."""
        writer_instance = MagicMock()
        mock_writer_class.return_value = writer_instance

        input_messages = [
            AirbyteMessage(
                type=Type.RECORD, record=AirbyteRecordMessage(stream="test", data={"data": {"content": "hello", "id": "1"}}, emitted_at=0)
            )
        ]

        list(self.destination.write(self.config, self.catalog, input_messages))

        # Verify delete_streams_to_overwrite was called before processing records
        writer_instance.delete_streams_to_overwrite.assert_called_once()
        self.assertEqual(writer_instance.method_calls[0][0], "delete_streams_to_overwrite")

    @patch("destination_ragie.destination.RagieClient")
    @patch("destination_ragie.destination.RagieWriter")
    def test_write_record_processing(self, mock_writer_class, mock_client_class):
        """Test that records are processed correctly."""
        writer_instance = MagicMock()
        mock_writer_class.return_value = writer_instance

        input_messages = [
            AirbyteMessage(
                type=Type.RECORD, record=AirbyteRecordMessage(stream="test", data={"data": {"content": "hello", "id": "1"}}, emitted_at=0)
            )
        ]

        # No state messages in this test case, so output should be empty
        output = list(self.destination.write(self.config, self.catalog, input_messages))

        # Verify record was queued for writing
        writer_instance.queue_write_operation.assert_called_once()
        self.assertEqual(len(output), 0)  # No state messages to yield
