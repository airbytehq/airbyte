# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import datetime
import hashlib
import json
import unittest
from unittest.mock import MagicMock, Mock, patch

from destination_ragie.writer import RagieWriter

from airbyte_cdk.models import (
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType


class TestRagieWriter(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.mock_config = Mock()

        # Mock config values
        self.mock_config.metadata_static_dict = {"source": "airbyte"}
        self.mock_config.content_fields = ["message"]
        self.mock_config.document_name_field = "doc.name"
        self.mock_config.metadata_fields = ["meta.author", "meta.tags"]
        self.mock_config.external_id_field = "external_id"
        self.mock_config.processing_mode = "fast"
        self.mock_config.partition = "test-partition"

        # Create a stream with proper AirbyteStream object
        stream = ConfiguredAirbyteStream(
            stream=AirbyteStream(
                name="my_stream", namespace="default", json_schema={"type": "object"}, supported_sync_modes=[SyncMode.incremental]
            ),
            destination_sync_mode=DestinationSyncMode.append_dedup,
            sync_mode=SyncMode.incremental,
        )
        self.mock_catalog = ConfiguredAirbyteCatalog(streams=[stream])

        # Setup writer
        self.writer = RagieWriter(client=self.mock_client, config=self.mock_config, catalog=self.mock_catalog)
        # Initialize write_buffer if not set in __init__
        if not hasattr(self.writer, "write_buffer"):
            self.writer.write_buffer = []

    def _make_record(self, message="hello", author="john", tags=None):
        if tags is None:
            tags = ["tag1", "tag2"]
        return AirbyteRecordMessage(
            stream="my_stream",
            namespace="default",
            emitted_at=int(datetime.datetime.now().timestamp() * 1000),
            data={"message": message, "doc": {"name": "my_doc"}, "meta": {"author": author, "tags": tags}},
        )

    def test_get_value_from_path(self):
        data = {"a": {"b": {"c": 123}}}
        result = self.writer._get_value_from_path(data, "a.b.c")
        self.assertEqual(result, 123)

    def test_calculate_content_hash_consistency(self):
        content = {"msg": "abc"}
        metadata = {"meta": "xyz"}
        hash1 = self.writer._calculate_content_hash(content, metadata)
        hash2 = self.writer._calculate_content_hash(content, metadata)
        self.assertEqual(hash1, hash2)

    def test_stream_tuple_to_id(self):
        result = self.writer._stream_tuple_to_id("namespace", "name")
        self.assertEqual(result, "namespace_name")

    def test_queue_write_operation_skips_duplicates(self):
        record = self._make_record()
        hash_val = self.writer._calculate_content_hash(
            {"message": "hello"},
            {
                "source": "airbyte",
                "meta_author": "john",
                "meta_tags": ["tag1", "tag2"],
                "airbyte_stream": "default_my_stream",
                "airbyte_content_hash": "dummy",
            },
        )
        self.writer.seen_hashes["default_my_stream"] = {hash_val}
        self.mock_client.find_docs_by_metadata.return_value = [{"metadata": {"airbyte_content_hash": hash_val}}]
        self.writer.queue_write_operation(record)
        self.assertEqual(len(self.writer.write_buffer), 0)

    def test_preload_hashes_if_needed_loads_hashes(self):
        self.mock_client.find_docs_by_metadata.return_value = [
            {"metadata": {"airbyte_content_hash": "abc"}},
            {"metadata": {"airbyte_content_hash": "def"}},
        ]
        self.writer._preload_hashes_if_needed("my_stream_id")
        self.assertIn("abc", self.writer.seen_hashes["my_stream_id"])
        self.assertIn("def", self.writer.seen_hashes["my_stream_id"])

    def test_delete_streams_to_overwrite_calls_delete(self):
        stream = ConfiguredAirbyteStream(
            stream=AirbyteStream(name="test", json_schema={"type": "object"}, supported_sync_modes=[SyncMode.full_refresh]),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.overwrite,
        )

        self.writer.streams = {"default_overwrite_stream": stream}
        self.mock_client.find_ids_by_metadata.return_value = ["id1", "id2"]
        self.writer.delete_streams_to_overwrite()
        self.assertCountEqual(self.mock_client.delete_documents_by_id.call_args[0][0], ["id1", "id2"])


if __name__ == "__main__":
    unittest.main()
