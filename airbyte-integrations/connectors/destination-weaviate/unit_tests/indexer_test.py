#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from collections import defaultdict
from unittest.mock import ANY, Mock, call, patch

from destination_weaviate.config import NoAuth, TokenAuth, WeaviateIndexingConfigModel
from destination_weaviate.indexer import WeaviateIndexer, WeaviatePartialBatchError

from airbyte_cdk.destinations.vector_db_based.document_processor import Chunk
from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage, DestinationSyncMode


class TestWeaviateIndexer(unittest.TestCase):
    def setUp(self):
        self.config = WeaviateIndexingConfigModel(
            host="https://test-host:12345", auth=TokenAuth(mode="token", token="abc")
        )  # Setup your config here
        self.indexer = WeaviateIndexer(self.config)
        mock_catalog = Mock()
        mock_stream = Mock()
        mock_stream.stream.name = "test"
        mock_stream.destination_sync_mode = DestinationSyncMode.append
        self.mock_stream = mock_stream
        mock_catalog.streams = [mock_stream]
        self.mock_catalog = mock_catalog

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
        self.assertEqual(self.indexer.check(), "Host must start with https:// and authentication must be enabled on cloud deployment.")

    @patch("destination_weaviate.indexer.os.environ")
    def test_failed_check_due_to_cloud_env_and_no_auth(self, mock_os_environ):
        mock_os_environ.get.return_value = "cloud"
        self.indexer.config.host = "http://example.com"
        self.indexer.config.auth = NoAuth(mode="no_auth")
        self.assertEqual(self.indexer.check(), "Host must start with https:// and authentication must be enabled on cloud deployment.")

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_pre_sync_that_creates_class(self, MockClient):
        mock_client = Mock()
        mock_client.schema.get.return_value = {"classes": []}
        MockClient.return_value = mock_client
        self.indexer.pre_sync(self.mock_catalog)
        mock_client.schema.create_class.assert_called_with(
            {
                "class": "Test",
                "vectorizer": "none",
                "properties": [
                    {
                        "name": "_ab_record_id",
                        "dataType": ["text"],
                        "description": "Record ID, used for bookkeeping.",
                        "indexFilterable": True,
                        "indexSearchable": False,
                        "tokenization": "field",
                    }
                ],
            }
        )

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_pre_sync_that_creates_class_with_multi_tenancy_enabled(self, MockClient):
        mock_client = Mock()
        self.config.tenant_id = "test_tenant"
        mock_client.schema.get_class_tenants.return_value = []
        mock_client.schema.get.return_value = {"classes": []}
        MockClient.return_value = mock_client
        self.indexer.pre_sync(self.mock_catalog)
        mock_client.schema.create_class.assert_called_with(
            {
                "class": "Test",
                "multiTenancyConfig": {"enabled": True},
                "vectorizer": "none",
                "properties": [
                    {
                        "name": "_ab_record_id",
                        "dataType": ["text"],
                        "description": "Record ID, used for bookkeeping.",
                        "indexFilterable": True,
                        "indexSearchable": False,
                        "tokenization": "field",
                    }
                ],
            }
        )

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_pre_sync_that_deletes(self, MockClient):
        mock_client = Mock()
        mock_client.schema.get.return_value = {
            "classes": [{"class": "Test", "properties": [{"name": "_ab_stream"}, {"name": "_ab_record_id"}]}]
        }
        MockClient.return_value = mock_client
        self.mock_stream.destination_sync_mode = DestinationSyncMode.overwrite
        self.indexer.pre_sync(self.mock_catalog)
        mock_client.schema.delete_class.assert_called_with(class_name="Test")
        mock_client.schema.create_class.assert_called_with(mock_client.schema.get.return_value["classes"][0])

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_pre_sync_no_delete_no_overwrite_mode(self, MockClient):
        mock_client = Mock()
        mock_client.schema.get.return_value = {
            "classes": [{"class": "Test", "properties": [{"name": "_ab_stream"}, {"name": "_ab_record_id"}]}]
        }
        MockClient.return_value = mock_client
        self.indexer.pre_sync(self.mock_catalog)
        mock_client.schema.delete_class.assert_not_called()

    def test_index_deletes_by_record_id(self):
        mock_client = Mock()
        self.indexer.client = mock_client
        self.indexer.has_record_id_metadata = defaultdict(None)
        self.indexer.has_record_id_metadata["Test"] = True
        self.indexer.delete(["some_id", "some_other_id"], None, "test")
        mock_client.batch.delete_objects.assert_called_with(
            class_name="Test",
            where={"path": ["_ab_record_id"], "operator": "ContainsAny", "valueStringArray": ["some_id", "some_other_id"]},
        )

    def test_index_deletes_by_record_id_with_tenant_id(self):
        mock_client = Mock()
        self.config.tenant_id = "test_tenant"
        self.indexer.client = mock_client
        self.indexer.has_record_id_metadata = defaultdict(None)
        self.indexer.has_record_id_metadata["Test"] = True
        self.indexer.delete(["some_id", "some_other_id"], None, "test")
        mock_client.batch.delete_objects.assert_called_with(
            class_name="Test",
            tenant="test_tenant",
            where={"path": ["_ab_record_id"], "operator": "ContainsAny", "valueStringArray": ["some_id", "some_other_id"]},
        )

    @patch("destination_weaviate.indexer.weaviate.Client")
    def test_index_not_delete_no_metadata_field(self, MockClient):
        mock_client = Mock()
        MockClient.return_value = mock_client
        self.indexer.has_record_id_metadata = defaultdict(None)
        self.indexer.has_record_id_metadata["Test"] = False
        self.indexer.delete(["some_id"], None, "test")
        mock_client.batch.delete_objects.assert_not_called()

    def test_index_flushes_batch(self):
        mock_client = Mock()
        self.indexer.client = mock_client
        mock_client.batch.create_objects.return_value = []
        mock_chunk1 = Chunk(
            page_content="some_content",
            embedding=[1, 2, 3],
            metadata={"someField": "some_value"},
            record=AirbyteRecordMessage(stream="test", data={"someField": "some_value"}, emitted_at=0),
        )
        mock_chunk2 = Chunk(
            page_content="some_other_content",
            embedding=[4, 5, 6],
            metadata={"someField": "some_value2"},
            record=AirbyteRecordMessage(stream="test", data={"someField": "some_value"}, emitted_at=0),
        )
        self.indexer.index([mock_chunk1, mock_chunk2], None, "test")
        mock_client.batch.create_objects.assert_called()
        chunk1_call = call({"someField": "some_value", "text": "some_content"}, "Test", ANY, vector=[1, 2, 3])
        chunk2_call = call({"someField": "some_value2", "text": "some_other_content"}, "Test", ANY, vector=[4, 5, 6])
        mock_client.batch.add_data_object.assert_has_calls([chunk1_call, chunk2_call], any_order=False)

    def test_index_splits_batch(self):
        mock_client = Mock()
        self.indexer.client = mock_client
        mock_client.batch.create_objects.return_value = []
        self.indexer.config.batch_size = 2
        mock_chunk1 = Chunk(
            page_content="some_content",
            embedding=[1, 2, 3],
            metadata={"someField": "some_value"},
            record=AirbyteRecordMessage(stream="test", data={"someField": "some_value"}, emitted_at=0),
        )
        mock_chunk2 = Chunk(
            page_content="some_other_content",
            embedding=[4, 5, 6],
            metadata={"someField": "some_value2"},
            record=AirbyteRecordMessage(stream="test", data={"someField": "some_value2"}, emitted_at=0),
        )
        mock_chunk3 = Chunk(
            page_content="third",
            embedding=[7, 8, 9],
            metadata={"someField": "some_value3"},
            record=AirbyteRecordMessage(stream="test", data={"someField": "some_value3"}, emitted_at=0),
        )
        self.indexer.index([mock_chunk1, mock_chunk2, mock_chunk3], None, "test")
        assert mock_client.batch.create_objects.call_count == 2

    def test_index_on_empty_batch(self):
        mock_client = Mock()
        self.indexer.client = mock_client
        self.indexer.index([], None, "test")
        assert mock_client.batch.create_objects.call_count == 0

    @patch("destination_weaviate.indexer.uuid.uuid4")
    @patch("time.sleep", return_value=None)
    def test_index_flushes_batch_and_propagates_error(self, MockTime, MockUUID):
        mock_client = Mock()
        self.indexer.client = mock_client
        mock_client.batch.create_objects.return_value = [{"result": {"errors": ["some_error"]}, "id": "some_id"}]
        MockUUID.side_effect = ["some_id", "some_id2"]
        mock_chunk1 = Chunk(
            page_content="some_content",
            embedding=[1, 2, 3],
            metadata={"someField": "some_value"},
            record=AirbyteRecordMessage(stream="test", data={"someField": "some_value"}, emitted_at=0),
        )
        mock_chunk2 = Chunk(
            page_content="some_other_content",
            embedding=[4, 5, 6],
            metadata={"someField": "some_value2"},
            record=AirbyteRecordMessage(stream="test", data={"someField": "some_value"}, emitted_at=0),
        )
        with self.assertRaises(WeaviatePartialBatchError):
            self.indexer.index([mock_chunk1, mock_chunk2], None, "test")
        chunk1_call = call({"someField": "some_value", "text": "some_content"}, "Test", "some_id", vector=[1, 2, 3])
        self.assertEqual(mock_client.batch.create_objects.call_count, 1)
        mock_client.batch.add_data_object.assert_has_calls([chunk1_call], any_order=False)

    def test_index_flushes_batch_and_normalizes(self):
        mock_client = Mock()
        self.indexer.client = mock_client
        mock_client.batch.create_objects.return_value = []
        mock_chunk = Chunk(
            page_content="some_content",
            embedding=[1, 2, 3],
            metadata={
                "someField": "some_value",
                "complex": {"a": [1, 2, 3]},
                "UPPERCASE_NAME": "abc",
                "id": 12,
                "empty_list": [],
                "referral Agency Name": "test1",
                "123StartsWithNumber": "test2",
                "special&*chars": "test3",
                "with spaces": "test4",
                "": "test5",
                "_startsWithUnderscore": "test6",
                "multiple  spaces": "test7",
                "SpecialCharacters!@#": "test8",
            },
            record=AirbyteRecordMessage(stream="test", data={"someField": "some_value"}, emitted_at=0),
        )
        self.indexer.index([mock_chunk], None, "test")
        mock_client.batch.add_data_object.assert_called_with(
            {
                "someField": "some_value",
                "complex": '{"a": [1, 2, 3]}',
                "uPPERCASE_NAME": "abc",
                "text": "some_content",
                "raw_id": 12,
                "referral_Agency_Name": "test1",
                "_123StartsWithNumber": "test2",
                "specialchars": "test3",
                "with_spaces": "test4",
                "_": "test5",
                "_startsWithUnderscore": "test6",
                "multiple__spaces": "test7",
                "specialCharacters": "test8",
            },
            "Test",
            ANY,
            vector=[1, 2, 3],
        )
