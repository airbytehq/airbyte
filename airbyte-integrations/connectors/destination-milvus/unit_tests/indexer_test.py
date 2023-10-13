#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import unittest
from unittest.mock import Mock, call

from airbyte_cdk.models.airbyte_protocol import AirbyteStream, DestinationSyncMode, SyncMode
from destination_milvus.config import MilvusIndexingConfigModel, NoAuth, TokenAuth
from destination_milvus.indexer import MilvusIndexer
from pymilvus import DataType
from pymilvus.exceptions import DescribeCollectionException


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
        self.milvus_indexer._create_client = Mock()  # This is mocked out because testing separate processes is hard
        self.milvus_indexer._collection = Mock()

    def test_check_returns_expected_result(self):
        self.milvus_indexer._collection.describe.return_value = {
            "auto_id": True,
            "fields": [{"name": "vector", "type": DataType.FLOAT_VECTOR, "params": {"dim": 128}}],
        }

        result = self.milvus_indexer.check()

        self.assertIsNone(result)

        self.milvus_indexer._collection.describe.assert_called()

    def test_check_secure_endpoint(self):
        self.milvus_indexer._collection.describe.return_value = {
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

    def test_check_handles_failure_conditions(self):
        # Test 1: Collection does not exist
        self.milvus_indexer._collection.describe.side_effect = DescribeCollectionException("Some error")

        result = self.milvus_indexer.check()
        self.assertEqual(result, f"Collection {self.mock_config.collection} does not exist")

        # Test 2: General exception in describe
        self.milvus_indexer._collection.describe.side_effect = Exception("Random exception")
        result = self.milvus_indexer.check()
        self.assertTrue("Random exception" in result)  # Assuming format_exception includes the exception message

        # Test 3: auto_id is not True
        self.milvus_indexer._collection.describe.return_value = {"auto_id": False}
        self.milvus_indexer._collection.describe.side_effect = None
        result = self.milvus_indexer.check()
        self.assertEqual(result, "Only collections with auto_id are supported")

        # Test 4: Vector field not found
        self.milvus_indexer._collection.describe.return_value = {"auto_id": True, "fields": [{"name": "wrong_vector_field"}]}
        result = self.milvus_indexer.check()
        self.assertEqual(result, f"Vector field {self.mock_config.vector_field} not found")

        # Test 5: Vector field is not a vector
        self.milvus_indexer._collection.describe.return_value = {
            "auto_id": True,
            "fields": [{"name": self.mock_config.vector_field, "type": DataType.INT32}],
        }
        result = self.milvus_indexer.check()
        self.assertEqual(result, f"Vector field {self.mock_config.vector_field} is not a vector")

        # Test 6: Vector field dimension mismatch
        self.milvus_indexer._collection.describe.return_value = {
            "auto_id": True,
            "fields": [{"name": self.mock_config.vector_field, "type": DataType.FLOAT_VECTOR, "params": {"dim": 64}}],
        }
        result = self.milvus_indexer.check()
        self.assertEqual(result, f"Vector field {self.mock_config.vector_field} is not a 128-dimensional vector")

    def test_pre_sync_calls_delete(self):
        mock_iterator = Mock()
        mock_iterator.next.side_effect = [[{"id": 1}], []]
        self.milvus_indexer._collection.query_iterator.return_value = mock_iterator

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

        self.milvus_indexer._collection.query_iterator.assert_called_with(expr='_ab_stream == "some_stream"')
        self.milvus_indexer._collection.delete.assert_called_with(expr="id in [1]")

    def test_pre_sync_does_not_call_delete(self):
        self.milvus_indexer.pre_sync(
            Mock(streams=[Mock(destination_sync_mode=DestinationSyncMode.append, stream=Mock(name="some_stream"))])
        )

        self.milvus_indexer._collection.delete.assert_not_called()

    def test_index_calls_insert(self):
        self.milvus_indexer._primary_key = "id"
        self.milvus_indexer.index(
            [Mock(metadata={"key": "value", "id": 5}, page_content="some content", embedding=[1, 2, 3])], None, "some_stream"
        )

        self.milvus_indexer._collection.insert.assert_called_with([{"key": "value", "vector": [1, 2, 3], "text": "some content", "_id": 5}])

    def test_index_calls_delete(self):
        mock_iterator = Mock()
        mock_iterator.next.side_effect = [[{"id": "123"}, {"id": "456"}], [{"id": "789"}], []]
        self.milvus_indexer._collection.query_iterator.return_value = mock_iterator

        self.milvus_indexer.delete(["some_id"], None, "some_stream")

        self.milvus_indexer._collection.query_iterator.assert_called_with(expr='_ab_record_id in ["some_id"]')
        self.milvus_indexer._collection.delete.assert_has_calls([call(expr="id in [123, 456]"), call(expr="id in [789]")], any_order=False)
