#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import unittest
from unittest.mock import Mock, call, patch

from airbyte_cdk.models.airbyte_protocol import AirbyteStream, DestinationSyncMode, SyncMode
from destination_milvus.config import MilvusIndexingConfigModel, NoAuth, TokenAuth
from destination_milvus.indexer import MilvusIndexer
from pymilvus import DataType


@patch("destination_milvus.indexer.connections")
@patch("destination_milvus.indexer.utility")
@patch("destination_milvus.indexer.Collection")
class TestMilvusIndexer(unittest.TestCase):
    def setUp(self):
        self.mock_config = MilvusIndexingConfigModel(
            **{
                "host": "https://notmilvus.com",
                "collection": "test2",
                "auth": {
                    "mode": "token",
                    "token": "mytoken",
                },
                "vector_field": "vector",
                "text_field": "text",
            }
        )
        self.milvus_indexer = MilvusIndexer(self.mock_config, 128)
        self.milvus_indexer._connect_with_timeout = Mock()  # Mocking this out to avoid testing multiprocessing
        self.milvus_indexer._collection = Mock()

    def test_check_returns_expected_result(self, mock_Collection, mock_utility, mock_connections):
        mock_Collection.return_value.describe.return_value = {
            "auto_id": True,
            "fields": [{"name": "vector", "type": DataType.FLOAT_VECTOR, "params": {"dim": 128}}],
        }

        result = self.milvus_indexer.check()

        self.assertIsNone(result)

        mock_Collection.return_value.describe.assert_called()

    def test_check_secure_endpoint(self, mock_Collection, mock_utility, mock_connections):
        mock_Collection.return_value.describe.return_value = {
            "auto_id": True,
            "fields": [{"name": "vector", "type": DataType.FLOAT_VECTOR, "params": {"dim": 128}}],
        }
        test_cases = [
            (
                "cloud",
                "http://example.org",
                TokenAuth(mode="token", token="abc"),
                "Host must start with https:// and authentication must be enabled on cloud deployment.",
            ),
            (
                "cloud",
                "https://example.org",
                NoAuth(mode="no_auth"),
                "Host must start with https:// and authentication must be enabled on cloud deployment.",
            ),
            ("cloud", "https://example.org", TokenAuth(mode="token", token="abc"), None),
            ("", "http://example.org", TokenAuth(mode="token", token="abc"), None),
            ("", "https://example.org", TokenAuth(mode="token", token="abc"), None),
            ("", "https://example.org", NoAuth(mode="no_auth"), None),
        ]
        for deployment_mode, uri, auth, expected_error_message in test_cases:
            os.environ["DEPLOYMENT_MODE"] = deployment_mode
            self.milvus_indexer.config.host = uri
            self.milvus_indexer.config.auth = auth

            result = self.milvus_indexer.check()

            self.assertEqual(result, expected_error_message)

    def test_check_handles_failure_conditions(self, mock_Collection, mock_utility, mock_connections):
        # Test 1: General exception in describe
        mock_Collection.return_value.describe.side_effect = Exception("Random exception")
        result = self.milvus_indexer.check()
        self.assertTrue("Random exception" in result)  # Assuming format_exception includes the exception message

        # Test 2: auto_id is not True
        mock_Collection.return_value.describe.return_value = {"auto_id": False}
        mock_Collection.return_value.describe.side_effect = None
        result = self.milvus_indexer.check()
        self.assertEqual(result, "Only collections with auto_id are supported")

        # Test 3: Vector field not found
        mock_Collection.return_value.describe.return_value = {"auto_id": True, "fields": [{"name": "wrong_vector_field"}]}
        result = self.milvus_indexer.check()
        self.assertEqual(result, f"Vector field {self.mock_config.vector_field} not found")

        # Test 4: Vector field is not a vector
        mock_Collection.return_value.describe.return_value = {
            "auto_id": True,
            "fields": [{"name": self.mock_config.vector_field, "type": DataType.INT32}],
        }
        result = self.milvus_indexer.check()
        self.assertEqual(result, f"Vector field {self.mock_config.vector_field} is not a vector")

        # Test 5: Vector field dimension mismatch
        mock_Collection.return_value.describe.return_value = {
            "auto_id": True,
            "fields": [{"name": self.mock_config.vector_field, "type": DataType.FLOAT_VECTOR, "params": {"dim": 64}}],
        }
        result = self.milvus_indexer.check()
        self.assertEqual(result, f"Vector field {self.mock_config.vector_field} is not a 128-dimensional vector")

    def test_pre_sync_creates_collection(self, mock_Collection, mock_utility, mock_connections):
        self.milvus_indexer.config.collection = "ad_hoc"
        self.milvus_indexer.config.vector_field = "my_vector_field"
        mock_utility.has_collection.return_value = False
        self.milvus_indexer.pre_sync(
            Mock(streams=[Mock(destination_sync_mode=DestinationSyncMode.append, stream=Mock(name="some_stream"))])
        )
        mock_Collection.assert_has_calls([call("ad_hoc")])
        mock_Collection.return_value.create_index.assert_has_calls(
            [call(field_name="my_vector_field", index_params={"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}})]
        )

    def test_pre_sync_calls_delete(self, mock_Collection, mock_utility, mock_connections):
        mock_iterator = Mock()
        mock_iterator.next.side_effect = [[{"id": 1}], []]
        mock_Collection.return_value.query_iterator.return_value = mock_iterator

        self.milvus_indexer.pre_sync(
            Mock(
                streams=[
                    Mock(
                        destination_sync_mode=DestinationSyncMode.overwrite,
                        stream=AirbyteStream(name="some_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                    )
                ]
            )
        )

        mock_Collection.return_value.query_iterator.assert_called_with(expr='_ab_stream == "some_stream"')
        mock_Collection.return_value.delete.assert_called_with(expr="id in [1]")

    def test_pre_sync_does_not_call_delete(self, mock_Collection, mock_utility, mock_connections):
        self.milvus_indexer.pre_sync(
            Mock(streams=[Mock(destination_sync_mode=DestinationSyncMode.append, stream=Mock(name="some_stream"))])
        )

        mock_Collection.return_value.delete.assert_not_called()

    def test_index_calls_insert(self, mock_Collection, mock_utility, mock_connections):
        self.milvus_indexer._primary_key = "id"
        self.milvus_indexer.index(
            [Mock(metadata={"key": "value", "id": 5}, page_content="some content", embedding=[1, 2, 3])], None, "some_stream"
        )

        self.milvus_indexer._collection.insert.assert_called_with([{"key": "value", "vector": [1, 2, 3], "text": "some content", "_id": 5}])

    def test_index_calls_delete(self, mock_Collection, mock_utility, mock_connections):
        mock_iterator = Mock()
        mock_iterator.next.side_effect = [[{"id": "123"}, {"id": "456"}], [{"id": "789"}], []]
        self.milvus_indexer._collection.query_iterator.return_value = mock_iterator

        self.milvus_indexer.delete(["some_id"], None, "some_stream")

        self.milvus_indexer._collection.query_iterator.assert_called_with(expr='_ab_record_id in ["some_id"]')
        self.milvus_indexer._collection.delete.assert_has_calls([call(expr="id in [123, 456]"), call(expr="id in [789]")], any_order=False)
