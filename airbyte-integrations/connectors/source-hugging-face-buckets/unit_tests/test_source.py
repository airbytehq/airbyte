#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import unittest
from unittest.mock import MagicMock, patch

from fsspec.implementations.memory import MemoryFileSystem
from source_hugging_face_buckets.source import SourceHuggingFaceBuckets

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, Status, Type


class TestSourceHuggingFaceBucketsCheck(unittest.TestCase):
    """Tests for the SourceHuggingFaceBuckets class."""

    def setUp(self):
        self.source = SourceHuggingFaceBuckets()

    @patch("source_hugging_face_buckets.source.HfFileSystem")
    def test_check_connection_success(self, mock_fs):
        """Test successful connection check."""
        mock_fs_instance = MagicMock()
        mock_fs_instance.ls.return_value = [{"name": "test/file.parquet", "type": "file"}]
        mock_fs.return_value = mock_fs_instance

        config = {
            "bucket_path": "hf://buckets/test/bucket/",
            "file_format": "parquet",
        }

        result = self.source.check(MagicMock(), config)
        self.assertEqual(result.status, Status.SUCCEEDED)

    @patch("source_hugging_face_buckets.source.HfFileSystem")
    def test_check_connection_failure(self, mock_fs):
        """Test failed connection check."""
        mock_fs_instance = MagicMock()
        mock_fs_instance.ls.side_effect = Exception("Access denied")
        mock_fs.return_value = mock_fs_instance

        config = {
            "bucket_path": "hf://buckets/test/bucket/",
            "file_format": "parquet",
        }

        result = self.source.check(MagicMock(), config)
        self.assertEqual(result.status, Status.FAILED)


class TestSourceHuggingFaceBucketsRead(unittest.TestCase):
    """Tests for the SourceHuggingFaceBuckets class."""

    def setUp(self):
        self.source = SourceHuggingFaceBuckets()

    @patch("source_hugging_face_buckets.source.HfFileSystem")
    def test_read(self, mock_fs):
        """Test read."""
        mock_fs_instance = MemoryFileSystem(skip_instance_cache=True)
        with mock_fs_instance.open("buckets/test/bucket/file.jsonl", "w") as f:
            f.write(json.dumps({"col1": "value1", "col2": 123}))
        mock_fs.return_value = mock_fs_instance

        config = {
            "bucket_path": "hf://buckets/test/bucket/",
            "file_format": "jsonl",
        }

        catalog = self.source.discover(MagicMock(), config)
        configured_catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(stream=stream, sync_mode="full_refresh", destination_sync_mode="overwrite")
                for stream in catalog.streams
            ]
        )
        result = list(self.source.read(MagicMock(), config, configured_catalog))

        record_messages = [m for m in result if m.type == Type.RECORD]
        self.assertEqual(len(record_messages), 1)
        self.assertDictEqual(record_messages[0].record.data, {"col1": "value1", "col2": 123})


if __name__ == "__main__":
    unittest.main()
