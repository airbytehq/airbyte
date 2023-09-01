#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import unittest
from unittest.mock import Mock

from airbyte_cdk.models.airbyte_protocol import AirbyteStream, DestinationSyncMode, SyncMode
from destination_milvus.config import MilvusIndexingConfigModel
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
        self.mock_embedder = Mock()
        self.mock_embedder.embedding_dimensions = 128
        self.milvus_indexer = MilvusIndexer(self.mock_config, self.mock_embedder)
        self.milvus_indexer._create_client = Mock()
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
            ("cloud", "http://example.org", "Host must start with https://"),
            ("cloud", "https://example.org", None),
            ("", "http://example.org", None),
            ("", "https://example.org", None)
        ]
        for deployment_mode, uri, expected_error_message in test_cases:
            os.environ["DEPLOYMENT_MODE"] = deployment_mode
            self.milvus_indexer.config.host = uri

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
        self.assertEqual(
            result, f"Vector field {self.mock_config.vector_field} is not a {self.mock_embedder.embedding_dimensions}-dimensional vector"
        )

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
        self.mock_embedder.embed_texts.return_value = [[1, 2, 3]]
        self.milvus_indexer.index([Mock(metadata={"key": "value"}, page_content="some content")], [])

        self.mock_embedder.embed_texts.assert_called_with(["some content"])
        self.milvus_indexer._collection.insert.assert_called_with(
            [{"key": "value", "vector": self.mock_embedder.embed_texts.return_value[0], "text": "some content"}]
        )

    def test_index_calls_delete(self):
        mock_iterator = Mock()
        mock_iterator.next.side_effect = [[{"id": "123"}], []]
        self.milvus_indexer._collection.query_iterator.return_value = mock_iterator

        self.milvus_indexer.index([], ["some_id"])

        self.milvus_indexer._collection.query_iterator.assert_called_with(expr='_ab_record_id in ["some_id"]')
        self.milvus_indexer._collection.delete.assert_called_with(expr="id in [123]")
