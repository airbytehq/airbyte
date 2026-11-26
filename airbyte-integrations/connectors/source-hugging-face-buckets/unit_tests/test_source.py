#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import unittest
from unittest.mock import MagicMock, patch

import pyarrow as pa
import pyarrow.parquet as pq
from fsspec.implementations.memory import MemoryFileSystem
from source_hugging_face_buckets.source import SourceHuggingFaceBuckets

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Status,
    SyncMode,
    Type,
)


def _isolated_memory_fs() -> MemoryFileSystem:
    """Get an in-memory filesystem with its own store.

    fsspec keeps the MemoryFileSystem store in a class level dict, so instances would otherwise
    share every file written by the other tests.
    """
    fs = MemoryFileSystem(skip_instance_cache=True)
    fs.store = {}
    return fs


def _configured_catalog(catalog: ConfiguredAirbyteCatalog) -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode="overwrite")
            for stream in catalog.streams
        ]
    )


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
        configured_catalog = _configured_catalog(catalog)
        result = list(self.source.read(MagicMock(), config, configured_catalog))

        record_messages = [m for m in result if m.type == Type.RECORD]
        self.assertEqual(len(record_messages), 1)
        self.assertDictEqual(record_messages[0].record.data, {"col1": "value1", "col2": 123})


class TestSourceHuggingFaceBucketsDiscovery(unittest.TestCase):
    """Tests for the stream names and schemas a bucket yields."""

    def setUp(self):
        self.source = SourceHuggingFaceBuckets()
        self.config = {"bucket_path": "hf://buckets/test/bucket/", "file_format": "parquet"}

    @patch("source_hugging_face_buckets.source.HfFileSystem")
    def test_streams_are_named_after_their_file(self, mock_fs):
        """Test readable stream names that stay stable between discovery and reads."""
        fs_instance = _isolated_memory_fs()
        for name in ("train.parquet", "test.parquet", ".hidden.parquet"):
            fs_instance.pipe_file(f"buckets/test/bucket/{name}", b"not read")
        mock_fs.return_value = fs_instance

        catalog = self.source.discover(MagicMock(), self.config)

        self.assertEqual(sorted(stream.name for stream in catalog.streams), ["test_parquet", "train_parquet"])

    @patch("source_hugging_face_buckets.source.HfFileSystem")
    def test_file_names_colliding_on_a_stream_name_stay_distinct(self, mock_fs):
        """Test that two files cannot share a stream name."""
        fs_instance = _isolated_memory_fs()
        for name in ("a.b.parquet", "a_b.parquet"):
            fs_instance.pipe_file(f"buckets/test/bucket/{name}", b"not read")
        mock_fs.return_value = fs_instance

        catalog = self.source.discover(MagicMock(), self.config)

        self.assertEqual(sorted(stream.name for stream in catalog.streams), ["a_b_parquet", "a_b_parquet__2"])

    @patch("source_hugging_face_buckets.source.HfFileSystem")
    def test_parquet_columns_are_discovered_with_their_types(self, mock_fs):
        """Test that the schema of a Parquet file describes the records it yields."""
        fs_instance = _isolated_memory_fs()
        table = pa.Table.from_pylist(
            [
                {"count": 1, "score": 1.5, "flag": True, "name": "a", "tags": ["x"], "meta": {"k": "v"}, "when": "2026-01-02"},
            ]
        )
        with fs_instance.open("buckets/test/bucket/train.parquet", "wb") as f:
            pq.write_table(table, f)
        mock_fs.return_value = fs_instance

        catalog = self.source.discover(MagicMock(), self.config)
        properties = catalog.streams[0].json_schema["properties"]

        self.assertEqual(properties["count"]["type"], ["integer", "null"])
        self.assertEqual(properties["score"]["type"], ["number", "null"])
        self.assertEqual(properties["flag"]["type"], ["boolean", "null"])
        self.assertEqual(properties["name"]["type"], ["string", "null"])
        self.assertEqual(properties["tags"]["type"], ["array", "null"])
        self.assertEqual(properties["meta"]["type"], ["object", "null"])

    @patch("source_hugging_face_buckets.source.HfFileSystem")
    def test_read_records_of_a_parquet_file_match_the_discovered_schema(self, mock_fs):
        """Test that discovery and a read of the same file agree on the data."""
        fs_instance = _isolated_memory_fs()
        table = pa.Table.from_pylist([{"count": 1, "tags": ["x", "y"]}, {"count": 2, "tags": []}])
        with fs_instance.open("buckets/test/bucket/train.parquet", "wb") as f:
            pq.write_table(table, f)
        mock_fs.return_value = fs_instance

        catalog = self.source.discover(MagicMock(), self.config)
        messages = list(self.source.read(MagicMock(), self.config, _configured_catalog(catalog)))

        records = [m.record.data for m in messages if m.type == Type.RECORD]
        self.assertEqual(records, [{"count": 1, "tags": ["x", "y"]}, {"count": 2, "tags": []}])

    @patch("source_hugging_face_buckets.source.HfFileSystem")
    def test_read_skips_a_stream_whose_file_is_gone(self, mock_fs):
        """Test that a catalog pointing at a deleted file does not fail the sync."""
        fs_instance = _isolated_memory_fs()
        fs_instance.pipe_file("buckets/test/bucket/present.parquet", b"not read")
        mock_fs.return_value = fs_instance

        stream = AirbyteStream(
            name="gone_parquet",
            json_schema=self.source._permissive_schema(),
            supported_sync_modes=[SyncMode.full_refresh],
        )
        catalog = ConfiguredAirbyteCatalog(
            streams=[ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode="overwrite")]
        )

        messages = list(self.source.read(MagicMock(), self.config, catalog))

        self.assertEqual([m for m in messages if m.type == Type.RECORD], [])

    def test_reader_options_must_be_a_json_object(self):
        """Test that unreadable reader options are ignored instead of failing the sync."""
        self.assertEqual(self.source._parse_reader_options({"reader_options": '{"sep": ";"}'}), {"sep": ";"})
        self.assertEqual(self.source._parse_reader_options({}), {})
        self.assertEqual(self.source._parse_reader_options({"reader_options": "not json"}), {})
        self.assertEqual(self.source._parse_reader_options({"reader_options": "[1, 2]"}), {})


if __name__ == "__main__":
    unittest.main()
