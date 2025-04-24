#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import Mock, call

from destination_qdrant.config import QdrantIndexingConfigModel
from destination_qdrant.indexer import QdrantIndexer
from qdrant_client import models

from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from airbyte_cdk.models.airbyte_protocol import AirbyteLogMessage, AirbyteMessage, AirbyteStream, DestinationSyncMode, Level, SyncMode, Type


class TestQdrantIndexer(unittest.TestCase):
    def setUp(self):
        self.mock_config = QdrantIndexingConfigModel(
            **{
                "url": "https://client-url.io",
                "auth_method": {"mode": "api_key_auth", "api_key": "api_key"},
                "prefer_grpc": False,
                "collection": "dummy-collection",
                "distance_metric": "dot",
                "text_field": "text",
            }
        )
        self.qdrant_indexer = QdrantIndexer(self.mock_config, 100)
        self.qdrant_indexer._create_client = Mock()
        self.qdrant_indexer._client = Mock()

    def test_check_gets_existing_collection(self):
        mock_collections = Mock(collections=[Mock()])
        mock_collections.collections[0].name = "dummy-collection"
        self.qdrant_indexer._client.get_collections.return_value = mock_collections

        self.qdrant_indexer._client.get_collection.return_value = Mock(
            config=Mock(params=Mock(vectors=Mock(size=100, distance=models.Distance.DOT)))
        )

        check_result = self.qdrant_indexer.check()

        self.assertIsNone(check_result)

        self.qdrant_indexer._create_client.assert_called()
        self.qdrant_indexer._client.get_collections.assert_called()
        self.qdrant_indexer._client.get_collection.assert_called()
        self.qdrant_indexer._client.close.assert_called()

    def test_check_creates_new_collection_if_not_exists(self):
        self.qdrant_indexer._client.get_collections.return_value = Mock(collections=[])
        check_result = self.qdrant_indexer.check()

        self.assertIsNone(check_result)

        self.qdrant_indexer._create_client.assert_called()
        self.qdrant_indexer._client.get_collections.assert_called()
        self.qdrant_indexer._client.recreate_collection.assert_called()
        self.qdrant_indexer._client.close.assert_called()

    def test_check_handles_failure_conditions(self):
        # Test 1: url starts with https://
        self.qdrant_indexer.config.url = "client-url.io"
        result = self.qdrant_indexer.check()
        self.assertEqual(result, "Host must start with https://")

        # Test 2: random exception
        self.qdrant_indexer.config.url = "https://client-url.io"
        self.qdrant_indexer._create_client.side_effect = Exception("Random exception")
        result = self.qdrant_indexer.check()
        self.assertTrue("Random exception" in result)

        # Test 3: client server is not alive
        self.qdrant_indexer._create_client.side_effect = None
        self.qdrant_indexer._client = None
        result = self.qdrant_indexer.check()
        self.assertEqual(result, "Qdrant client is not alive.")

        # Test 4: Test vector size does not match
        mock_collections = Mock(collections=[Mock()])
        mock_collections.collections[0].name = "dummy-collection"

        self.qdrant_indexer._client = Mock()
        self.qdrant_indexer._client.get_collections.return_value = mock_collections
        self.qdrant_indexer._client.get_collection.return_value = Mock(
            config=Mock(params=Mock(vectors=Mock(size=10, distance=models.Distance.DOT)))
        )

        result = self.qdrant_indexer.check()
        self.assertTrue("The collection's vector's size must match the embedding dimensions" in result)

        # Test 5: Test distance metric does not match
        self.qdrant_indexer._client.get_collection.return_value = Mock(
            config=Mock(params=Mock(vectors=Mock(size=100, distance=models.Distance.COSINE)))
        )
        result = self.qdrant_indexer.check()
        self.assertTrue("The colection's vector's distance metric must match the selected distance metric option" in result)

    def test_pre_sync_calls_delete(self):
        self.qdrant_indexer.pre_sync(
            Mock(
                streams=[
                    Mock(
                        destination_sync_mode=DestinationSyncMode.overwrite,
                        stream=AirbyteStream(name="some_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                    ),
                    Mock(
                        destination_sync_mode=DestinationSyncMode.overwrite,
                        stream=AirbyteStream(name="another_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                    ),
                    Mock(
                        destination_sync_mode=DestinationSyncMode.append,
                        stream=AirbyteStream(name="incremental_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                    ),
                ]
            )
        )

        self.qdrant_indexer._client.delete.assert_called_with(
            collection_name=self.mock_config.collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    should=[
                        models.FieldCondition(key="_ab_stream", match=models.MatchValue(value="some_stream")),
                        models.FieldCondition(key="_ab_stream", match=models.MatchValue(value="another_stream")),
                    ]
                )
            ),
        )

    def test_pre_sync_does_not_call_delete(self):
        self.qdrant_indexer.pre_sync(
            Mock(streams=[Mock(destination_sync_mode=DestinationSyncMode.append, stream=Mock(name="some_stream"))])
        )

        self.qdrant_indexer._client.delete.assert_not_called()

    def test_pre_sync_calls_create_payload_index(self):
        self.qdrant_indexer.pre_sync(Mock(streams=[]))

        calls = [
            call(collection_name=self.mock_config.collection, field_name="_ab_record_id", field_schema="keyword"),
            call(collection_name=self.mock_config.collection, field_name="_ab_stream", field_schema="keyword"),
        ]

        self.qdrant_indexer._client.create_payload_index.assert_has_calls(calls)

    def test_index_calls_insert(self):
        self.qdrant_indexer.index(
            [
                Mock(metadata={"key": "value1"}, page_content="some content", embedding=[1.0, 2.0, 3.0]),
                Mock(metadata={"key": "value2"}, page_content="some other content", embedding=[4.0, 5.0, 6.0]),
            ],
            None,
            "some_stream",
        )

        self.qdrant_indexer._client.upload_records.assert_called_once()

    def test_index_calls_delete(self):
        self.qdrant_indexer.delete(["some_id", "another_id"], None, "some_stream")

        self.qdrant_indexer._client.delete.assert_called_with(
            collection_name=self.mock_config.collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    should=[
                        models.FieldCondition(key="_ab_record_id", match=models.MatchValue(value="some_id")),
                        models.FieldCondition(key="_ab_record_id", match=models.MatchValue(value="another_id")),
                    ]
                )
            ),
        )

    def test_post_sync_calls_close(self):
        result = self.qdrant_indexer.post_sync()
        self.qdrant_indexer._client.close.assert_called_once()
        self.assertEqual(
            result,
            [
                AirbyteMessage(
                    type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="Qdrant Database Client has been closed successfully")
                )
            ],
        )

    def test_post_sync_handles_failure(self):
        exception = Exception("Random exception")
        self.qdrant_indexer._client.close.side_effect = exception
        result = self.qdrant_indexer.post_sync()

        self.qdrant_indexer._client.close.assert_called_once()
        self.assertEqual(
            result, [AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.ERROR, message=format_exception(exception)))]
        )
