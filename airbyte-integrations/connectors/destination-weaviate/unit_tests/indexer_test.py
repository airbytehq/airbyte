#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from collections import defaultdict
from unittest.mock import ANY, MagicMock, Mock, call, patch

from destination_weaviate.config import NoAuth, TokenAuth, WeaviateIndexingConfigModel
from destination_weaviate.indexer import WeaviateIndexer, WeaviatePartialBatchError

from airbyte_cdk.destinations.vector_db_based.document_processor import Chunk
from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage, DestinationSyncMode


class TestWeaviateIndexer(unittest.TestCase):
    def setUp(self):
        self.config = WeaviateIndexingConfigModel(host="https://test-host:12345", auth=TokenAuth(mode="token", token="abc"))
        self.indexer = WeaviateIndexer(self.config)
        mock_catalog = Mock()
        mock_stream = Mock()
        mock_stream.stream.name = "test"
        mock_stream.destination_sync_mode = DestinationSyncMode.append
        self.mock_stream = mock_stream
        mock_catalog.streams = [mock_stream]
        self.mock_catalog = mock_catalog

    def _make_mock_client(self):
        """Return (mock_client, mock_batch_obj) with v4 batch context manager wired up."""
        mock_client = Mock()
        mock_batch_obj = Mock()
        mock_batch_ctx = MagicMock()
        mock_batch_ctx.__enter__ = Mock(return_value=mock_batch_obj)
        mock_batch_ctx.__exit__ = Mock(return_value=False)
        mock_client.batch.fixed_size.return_value = mock_batch_ctx
        mock_client.batch.failed_objects = []
        return mock_client, mock_batch_obj

    # ------------------------------------------------------------------
    # check()
    # ------------------------------------------------------------------

    @patch("destination_weaviate.indexer.weaviate.connect_to_weaviate_cloud")
    def test_successful_check(self, mock_connect):
        self.assertIsNone(self.indexer.check())
        mock_connect.assert_called_once()

    @patch("destination_weaviate.indexer.weaviate.connect_to_weaviate_cloud")
    def test_failed_check_due_to_exception(self, mock_connect):
        mock_connect.side_effect = Exception("Random exception")
        self.assertIsNotNone(self.indexer.check())

    @patch("destination_weaviate.indexer.os.environ")
    def test_failed_check_due_to_cloud_env_and_no_https_host(self, mock_os_environ):
        mock_os_environ.get.return_value = "cloud"
        self.indexer.config.host = "http://example.com"
        self.assertEqual(
            self.indexer.check(),
            "Host must start with https:// and authentication must be enabled on cloud deployment.",
        )

    @patch("destination_weaviate.indexer.os.environ")
    def test_failed_check_due_to_cloud_env_and_no_auth(self, mock_os_environ):
        mock_os_environ.get.return_value = "cloud"
        self.indexer.config.host = "http://example.com"
        self.indexer.config.auth = NoAuth(mode="no_auth")
        self.assertEqual(
            self.indexer.check(),
            "Host must start with https:// and authentication must be enabled on cloud deployment.",
        )

    # ------------------------------------------------------------------
    # pre_sync()
    # ------------------------------------------------------------------

    @patch("destination_weaviate.indexer.weaviate.connect_to_weaviate_cloud")
    def test_pre_sync_that_creates_class(self, mock_connect):
        mock_client = Mock()
        mock_client.collections.list_all.return_value = {}
        mock_connect.return_value = mock_client

        self.indexer.pre_sync(self.mock_catalog)

        mock_client.collections.create.assert_called_once()
        create_kwargs = mock_client.collections.create.call_args.kwargs
        self.assertEqual(create_kwargs["name"], "Test")
        self.assertIsNone(create_kwargs.get("multi_tenancy_config"))
        props = create_kwargs.get("properties", [])
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0].name, "_ab_record_id")

    @patch("destination_weaviate.indexer.weaviate.connect_to_weaviate_cloud")
    def test_pre_sync_that_creates_class_with_multi_tenancy_enabled(self, mock_connect):
        mock_client = Mock()
        self.config.tenant_id = "test_tenant"
        mock_client.collections.list_all.return_value = {}
        # Simulate no existing tenants for the new collection
        mock_client.collections.get.return_value.tenants.get.return_value = {}
        mock_connect.return_value = mock_client

        self.indexer.pre_sync(self.mock_catalog)

        mock_client.collections.create.assert_called_once()
        create_kwargs = mock_client.collections.create.call_args.kwargs
        self.assertEqual(create_kwargs["name"], "Test")
        self.assertIsNotNone(create_kwargs.get("multi_tenancy_config"))

    @patch("destination_weaviate.indexer.weaviate.connect_to_weaviate_cloud")
    def test_pre_sync_that_deletes(self, mock_connect):
        mock_client = Mock()
        mock_collection_config = Mock()
        mock_collection_config.properties = []
        mock_client.collections.list_all.return_value = {"Test": mock_collection_config}
        exported = {"class": "Test"}
        mock_client.collections.export_config.return_value.to_dict.return_value = exported
        mock_connect.return_value = mock_client

        self.mock_stream.destination_sync_mode = DestinationSyncMode.overwrite
        self.indexer.pre_sync(self.mock_catalog)

        mock_client.collections.delete.assert_called_with("Test")
        mock_client.collections.create_from_dict.assert_called_with(exported)

    @patch("destination_weaviate.indexer.weaviate.connect_to_weaviate_cloud")
    def test_pre_sync_no_delete_no_overwrite_mode(self, mock_connect):
        mock_client = Mock()
        prop_record_id = Mock()
        prop_record_id.name = "_ab_record_id"
        mock_collection_config = Mock()
        mock_collection_config.properties = [prop_record_id]
        mock_client.collections.list_all.return_value = {"Test": mock_collection_config}
        mock_connect.return_value = mock_client

        self.indexer.pre_sync(self.mock_catalog)

        mock_client.collections.delete.assert_not_called()
        self.assertTrue(self.indexer.has_record_id_metadata["Test"])

    # ------------------------------------------------------------------
    # delete()
    # ------------------------------------------------------------------

    def test_index_deletes_by_record_id(self):
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.collections.get.return_value = mock_collection
        self.indexer.client = mock_client
        self.indexer.has_record_id_metadata = defaultdict(lambda: False)
        self.indexer.has_record_id_metadata["Test"] = True

        self.indexer.delete(["some_id", "some_other_id"], None, "test")

        mock_client.collections.get.assert_called_with("Test")
        mock_collection.data.delete_many.assert_called_once()
        call_kwargs = mock_collection.data.delete_many.call_args.kwargs
        self.assertIn("where", call_kwargs)

    def test_index_deletes_by_record_id_with_tenant_id(self):
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.collections.get.return_value = mock_collection
        self.config.tenant_id = "test_tenant"
        self.indexer.client = mock_client
        self.indexer.has_record_id_metadata = defaultdict(lambda: False)
        self.indexer.has_record_id_metadata["Test"] = True

        self.indexer.delete(["some_id", "some_other_id"], None, "test")

        mock_collection.with_tenant.assert_called_with("test_tenant")
        mock_collection.with_tenant.return_value.data.delete_many.assert_called_once()

    def test_index_not_delete_no_metadata_field(self):
        mock_client = Mock()
        self.indexer.client = mock_client
        self.indexer.has_record_id_metadata = defaultdict(lambda: False)
        self.indexer.has_record_id_metadata["Test"] = False

        self.indexer.delete(["some_id"], None, "test")

        mock_client.collections.get.assert_not_called()

    # ------------------------------------------------------------------
    # index()
    # ------------------------------------------------------------------

    def test_index_flushes_batch(self):
        mock_client, mock_batch_obj = self._make_mock_client()
        self.indexer.client = mock_client

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

        self.assertEqual(mock_batch_obj.add_object.call_count, 2)

        call1_kwargs = mock_batch_obj.add_object.call_args_list[0].kwargs
        self.assertEqual(call1_kwargs["properties"], {"someField": "some_value", "text": "some_content"})
        self.assertEqual(call1_kwargs["collection"], "Test")
        self.assertEqual(call1_kwargs["vector"], [1, 2, 3])

        call2_kwargs = mock_batch_obj.add_object.call_args_list[1].kwargs
        self.assertEqual(call2_kwargs["properties"], {"someField": "some_value2", "text": "some_other_content"})
        self.assertEqual(call2_kwargs["collection"], "Test")
        self.assertEqual(call2_kwargs["vector"], [4, 5, 6])

    def test_index_splits_batch(self):
        mock_client, mock_batch_obj = self._make_mock_client()
        self.indexer.client = mock_client
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

        # Two batches: [chunk1, chunk2] and [chunk3]
        self.assertEqual(mock_client.batch.fixed_size.call_count, 2)

    def test_index_on_empty_batch(self):
        mock_client, _ = self._make_mock_client()
        self.indexer.client = mock_client

        self.indexer.index([], None, "test")

        mock_client.batch.fixed_size.assert_not_called()

    @patch("destination_weaviate.indexer.uuid.uuid4")
    def test_index_flushes_batch_and_propagates_error(self, MockUUID):
        mock_client, mock_batch_obj = self._make_mock_client()
        failed_obj = Mock()
        failed_obj.__str__ = Mock(return_value="some_error")
        mock_client.batch.failed_objects = [failed_obj]
        MockUUID.side_effect = ["some_id", "some_id2"]
        self.indexer.client = mock_client

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

        self.assertEqual(mock_batch_obj.add_object.call_count, 2)

    def test_index_flushes_batch_and_normalizes(self):
        mock_client, mock_batch_obj = self._make_mock_client()
        self.indexer.client = mock_client

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

        call_kwargs = mock_batch_obj.add_object.call_args.kwargs
        self.assertEqual(
            call_kwargs["properties"],
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
        )
        self.assertEqual(call_kwargs["collection"], "Test")
        self.assertEqual(call_kwargs["vector"], [1, 2, 3])
