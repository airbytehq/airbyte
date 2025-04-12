import unittest
from unittest.mock import Mock, MagicMock
from destination_ragie.writer import RagieWriter
from airbyte_cdk.models import ConfiguredAirbyteStream, ConfiguredAirbyteCatalog, AirbyteRecordMessage, DestinationSyncMode, SyncMode, AirbyteStream
import datetime


class TestRagieWriter(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.mock_config = Mock()

        # Mock config values
        self.mock_config.batch_size = 2
        self.mock_config.metadata_static = {"source": "airbyte"}
        self.mock_config.content_fields = ["message"]
        self.mock_config.document_name_field = "doc.name"
        self.mock_config.metadata_fields = ["meta.author", "meta.tags"]
        self.mock_config.processing_mode = "default"
        self.mock_config.partition = "test-partition"

        stream = ConfiguredAirbyteStream(
            stream=Mock(name="my_stream", namespace="default"),
            destination_sync_mode=DestinationSyncMode.append_dedup,
            sync_mode=SyncMode.incremental
        )
        self.mock_catalog = ConfiguredAirbyteCatalog(streams=[stream])

        self.writer = RagieWriter(
            client=self.mock_client,
            config=self.mock_config,
            catalog=self.mock_catalog
        )

    def _make_record(self, message="hello", author="john", tags=None):
        if tags is None:
            tags = ["tag1", "tag2"]
        return AirbyteRecordMessage(
            stream="my_stream",
            namespace="default",
            emitted_at=int(datetime.datetime.now().timestamp() * 1000),
            data={
                "message": message,
                "doc": {"name": "my_doc"},
                "meta": {"author": author, "tags": tags}
            }
        )

    def test_get_value_from_path(self):
        data = {"a": {"b": {"c": 123}}}
        result = self.writer._get_value_from_path(data, ["a", "b", "c"])
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

    def test_queue_write_operation_adds_to_buffer(self):
        record = self._make_record()
        self.mock_client.find_docs_by_metadata.return_value = []
        self.writer.queue_write_operation(record)
        self.assertEqual(len(self.writer.write_buffer), 1)

    def test_queue_write_operation_skips_duplicates(self):
        record = self._make_record()
        hash_val = self.writer._calculate_content_hash(
            {"message": "hello"},
            {
                "source": "airbyte",
                "meta_author": "john",
                "meta_tags": ["tag1", "tag2"],
                "airbyte_stream": "default_my_stream",
                "airbyte_content_hash": "dummy"
            }
        )
        self.writer.seen_hashes["default_my_stream"] = {hash_val}
        self.mock_client.find_docs_by_metadata.return_value = [{"metadata": {"airbyte_content_hash": hash_val}}]
        self.writer.queue_write_operation(record)
        self.assertEqual(len(self.writer.write_buffer), 0)

    def test_flush_sends_data_and_clears_buffer(self):
        self.mock_client.index_documents = MagicMock()
        record1 = self._make_record(message="one")
        record2 = self._make_record(message="two")
        self.mock_client.find_docs_by_metadata.return_value = []
        self.writer.queue_write_operation(record1)
        self.writer.queue_write_operation(record2)  # Should trigger flush
        self.mock_client.index_documents.assert_called_once()
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
            sync_mode=SyncMode.full_refresh,  # Add the sync_mode argument
            destination_sync_mode=[DestinationSyncMode.overwrite, DestinationSyncMode.append_dedup, DestinationSyncMode.append],
        )

        self.writer.streams = {
            "default_overwrite_stream": stream
        }
        self.mock_client.find_ids_by_metadata.return_value = ["id1", "id2"]
        self.writer.delete_streams_to_overwrite()
        self.mock_client.delete_documents_by_id.assert_called_with(["id1", "id2"])

    def test_check_connection_failure(self):
        # Assuming this method is expecting 'config', make sure it's passed
        result = self.writer.check(self.mock_config)
        self.assertFalse(result)  # Adjust the expected behavior

    def test_check_connection_success(self):
        # Assuming this method is expecting 'config', make sure it's passed
        result = self.writer.check(self.mock_config)
        self.assertTrue(result)  # Adjust the expected behavior

if __name__ == '__main__':
    unittest.main()
