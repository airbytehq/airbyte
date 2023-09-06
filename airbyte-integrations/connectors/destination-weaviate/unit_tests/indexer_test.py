import unittest
from unittest.mock import patch, Mock, MagicMock
from destination_weaviate.config import WeaviateIndexingConfigModel, NoAuth
from destination_weaviate.indexer import WeaviateIndexer
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from airbyte_cdk.destinations.vector_db_based.document_processor import Chunk

class TestWeaviateIndexer(unittest.TestCase):

    def setUp(self):
        self.config = WeaviateIndexingConfigModel(host="https://test-host:12345", class_name="Test", auth=NoAuth())  # Setup your config here
        self.indexer = WeaviateIndexer(self.config)

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_successful_check(self, MockClient):
        self.assertIsNone(self.indexer.check())

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_failed_check_due_to_exception(self, MockClient):
        MockClient.side_effect = Exception("Random exception")
        self.assertIsNotNone(self.indexer.check())

    @patch("destination_weaviate.indexer.os.environ")
    def test_failed_check_due_to_cloud_env_and_no_https_host(self, mock_os_environ):
        mock_os_environ.get.return_value = "cloud"
        self.indexer.config.host = "http://example.com"
        self.assertEqual(self.indexer.check(), "Host must start with https://")

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_pre_sync_that_deletes(self, MockClient):
        mock_client = Mock()
        MockClient.return_value = mock_client
        self.indexer.has_stream_metadata = True
        self.indexer.pre_sync(Mock())
        mock_client.batch.delete_objects.assert_called()

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_pre_sync_no_delete_no_metadata_field(self, MockClient):
        mock_client = Mock()
        MockClient.return_value = mock_client
        self.indexer.has_stream_metadata = False
        self.indexer.pre_sync(Mock())
        mock_client.batch.delete_objects.assert_not_called()

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_pre_sync_no_delete_no_overwrite_mode(self, MockClient):
        mock_client = Mock()
        MockClient.return_value = mock_client
        mock_catalog = Mock()
        mock_stream = Mock()
        mock_stream.destination_sync_mode = DestinationSyncMode.append
        mock_catalog.streams = [mock_stream]
        self.indexer.pre_sync(mock_catalog)
        mock_client.batch.delete_objects.assert_not_called()

    def test_index_deletes_by_record_id(self):
        mock_client = Mock()
        self.indexer.client = mock_client
        self.indexer.has_record_id_metadata = True
        self.indexer.index([], ["some_id", "some_other_id"])
        mock_client.batch.delete_objects.assert_called_with(class_name="Test", where={"path":["_ab_record_id"], "operator": "ContainsAny", "valueStringArray": ["some_id", "some_other_id"]})

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_index_not_delete_no_metadata_field(self, MockClient):
        mock_client = Mock()
        MockClient.return_value = mock_client
        self.indexer.has_record_id_metadata = False
        self.indexer.index([], ["some_id"])
        mock_client.batch.delete_objects.assert_not_called()

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_index_flushes_batch(self, MockClient):
        mock_client = Mock()
        MockClient.return_value = mock_client
        mock_chunk = Chunk()
        self.indexer.index([mock_chunk], [])
        self.indexer.flush()
        mock_client.batch.create_objects.assert_called()

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_index_flushes_batch_and_retries(self, MockClient):
        mock_client = Mock()
        MockClient.return_value = mock_client
        mock_client.batch.create_objects.return_value = [{'result': {'errors': ['some_error']}, 'id': 'some_id'}]
        mock_chunk = Chunk()
        self.indexer.index([mock_chunk], [])
        self.indexer.flush()
        self.assertEqual(mock_client.batch.create_objects.call_count, 4)  # 1 initial try + 3 retries

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_index_flushes_batch_and_normalizes(self, MockClient):
        mock_client = Mock()
        MockClient.return_value = mock_client
        mock_chunk = Chunk(metadata={'someField': {'nestedField': 'some_value'}})
        self.indexer.index([mock_chunk], [])
        self.indexer.flush()
        self.assertTrue(isinstance(self.indexer.buffered_objects['some_id'].properties['someField'], str))  # Should be JSON serialized

if __name__ == "__main__":
    unittest.main()
