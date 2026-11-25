#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock, patch

import pyarrow.parquet as pq
from destination_hugging_face_buckets.destination import (
    DestinationHuggingFaceBuckets,
)
from fsspec.implementations.memory import MemoryFileSystem

from airbyte_cdk.models import Status
from airbyte_cdk.utils import AirbyteTracedException


def _isolated_memory_fs() -> MemoryFileSystem:
    """Get an in-memory filesystem with its own store.

    fsspec keeps the MemoryFileSystem store in a class level dict, so instances would otherwise
    share every file written by the other tests.
    """
    fs = MemoryFileSystem(skip_instance_cache=True)
    fs.store = {}
    return fs


class TestDestinationHuggingFaceBucketsCheck(unittest.TestCase):
    """Tests for the DestinationHuggingFaceBuckets.check method."""

    def setUp(self):
        self.destination = DestinationHuggingFaceBuckets()

    @patch("destination_hugging_face_buckets.destination.HfFileSystem")
    def test_check_connection_success(self, mock_fs):
        """Test successful connection check."""
        mock_fs.return_value = _isolated_memory_fs()

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
    def test_write(self, mock_fs):
        """Test successful connection check."""
        mock_fs_instance = _isolated_memory_fs()
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
                ),
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

    @patch("destination_hugging_face_buckets.destination.HfFileSystem")
    def test_write_keeps_nested_values(self, mock_fs):
        """Test that records with nested objects and lists are written as they are."""
        fs_instance = _isolated_memory_fs()
        mock_fs.return_value = fs_instance

        from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, Type

        messages = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    data={"col1": "a", "nested": {"x": 1}, "items": [1, 2]},
                    stream="test_stream",
                    emitted_at=0,
                ),
            ),
        ]

        list(self.destination.write({"destination_path": "test/bucket/", "file_format": "parquet"}, MagicMock(), iter(messages)))

        written = fs_instance.glob("**/*.parquet")[0]
        table = pq.read_table(fs_instance.open(written, "rb"))
        self.assertEqual(table.column("items")[0].as_py(), [1, 2])
        self.assertEqual(table.column("nested")[0].as_py(), {"x": 1})

    @patch("destination_hugging_face_buckets.destination.pq.write_table")
    @patch("destination_hugging_face_buckets.destination.HfFileSystem")
    def test_write_fails_when_a_file_cannot_be_uploaded(self, mock_fs, mock_write_table):
        """Test that a failed upload fails the sync instead of dropping the records."""
        mock_fs.return_value = _isolated_memory_fs()
        mock_write_table.side_effect = OSError("the bucket is unreachable")

        from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, Type

        messages = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(data={"col1": "a"}, stream="test_stream", emitted_at=0),
            ),
        ]

        with self.assertRaises(AirbyteTracedException):
            list(self.destination.write({"destination_path": "test/bucket/", "file_format": "parquet"}, MagicMock(), iter(messages)))


if __name__ == "__main__":
    unittest.main()
