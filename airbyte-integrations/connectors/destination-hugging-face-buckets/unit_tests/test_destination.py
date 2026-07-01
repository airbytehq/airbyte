#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock, patch

from destination_hugging_face_buckets.destination import (
    DestinationHuggingFaceBuckets,
)
from fsspec.implementations.memory import MemoryFileSystem

from airbyte_cdk.models import Status


class TestDestinationHuggingFaceBucketsCheck(unittest.TestCase):
    """Tests for the DestinationHuggingFaceBuckets.check method."""

    def setUp(self):
        self.destination = DestinationHuggingFaceBuckets()

    @patch("destination_hugging_face_buckets.destination.HfFileSystem")
    def test_check_connection_success(
        self, mock_fs
    ):
        """Test successful connection check."""
        mock_fs.return_value = MemoryFileSystem(skip_instance_cache=True)

        config = {
            "destination_path": "hf://buckets/test/bucket/",
            "file_format": "parquet",
        }

        result = self.destination.check(MagicMock(), config)
        self.assertEqual(result.status, Status.SUCCEEDED)

    @patch("destination_hugging_face_buckets.destination.HfFileSystem.open")
    def test_check_connection_failure(self, mock_open):
        """Test failed connection check."""
        mock_open.side_effect = Exception("Access denied")

        config = {
            "destination_path": "hf://buckets/test/bucket/",
            "file_format": "parquet",
        }

        result = self.destination.check(MagicMock(), config)
        self.assertEqual(result.status, Status.FAILED)


class TestDestinationHuggingFaceBucketsWrite(unittest.TestCase):
    """Tests for the DestinationHuggingFaceBuckets.check method."""

    def setUp(self):
        self.destination = DestinationHuggingFaceBuckets()

    @patch("destination_hugging_face_buckets.destination.HfFileSystem")
    def test_write(
        self, mock_fs
    ):
        """Test successful connection check."""
        mock_fs_instance = MemoryFileSystem(skip_instance_cache=True)
        mock_fs.return_value = mock_fs_instance

        # Create mock messages
        from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, Type
        messages = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    data={"col1": "value1", "col2": 123},
                    stream="test_stream",
                    emitted_at=0,
                )
            ),
            AirbyteMessage(type=Type.STATE, state={"checkpoint": 1}),
        ]

        config = {
            "destination_path": "hf://buckets/test/bucket/",
            "file_format": "parquet",
        }

        result = list(self.destination.write(config, MagicMock(), iter(messages)))

        output_files = mock_fs_instance.glob("**/*.parquet")
        self.assertEqual(len(output_files), 1)

        # Verify state message was yielded
        state_messages = [m for m in result if m.type == Type.STATE]
        self.assertEqual(len(state_messages), 1)


if __name__ == "__main__":
    unittest.main()
