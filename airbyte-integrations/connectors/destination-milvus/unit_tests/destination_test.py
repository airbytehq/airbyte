#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock, Mock, patch

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification, Status
from destination_milvus.config import ConfigModel
from destination_milvus.destination import DestinationMilvus


class TestDestinationMilvus(unittest.TestCase):
    def setUp(self):
        self.config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {
                "host": "https://notmilvus.com",
                "collection": "test2",
                "auth": {
                    "mode": "token",
                    "token": "mytoken",
                },
                "vector_field": "vector",
                "text_field": "text",
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = AirbyteLogger()

    @patch("destination_milvus.destination.MilvusIndexer")
    @patch("destination_milvus.destination.create_from_config")
    def test_check(self, MockedEmbedder, MockedMilvusIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        MockedMilvusIndexer.return_value = mock_indexer

        mock_embedder.check.return_value = None
        mock_indexer.check.return_value = None

        destination = DestinationMilvus()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_milvus.destination.MilvusIndexer")
    @patch("destination_milvus.destination.create_from_config")
    def test_check_with_errors(self, MockedEmbedder, MockedMilvusIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        MockedMilvusIndexer.return_value = mock_indexer

        embedder_error_message = "Embedder Error"
        indexer_error_message = "Indexer Error"

        mock_embedder.check.return_value = embedder_error_message
        mock_indexer.check.return_value = indexer_error_message

        destination = DestinationMilvus()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.FAILED)
        self.assertEqual(result.message, f"{embedder_error_message}\n{indexer_error_message}")

        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_milvus.destination.Writer")
    @patch("destination_milvus.destination.MilvusIndexer")
    @patch("destination_milvus.destination.create_from_config")
    def test_write(self, MockedEmbedder, MockedMilvusIndexer, MockedWriter):
        mock_embedder = Mock()
        mock_indexer = Mock()
        mock_writer = Mock()

        MockedEmbedder.return_value = mock_embedder
        MockedMilvusIndexer.return_value = mock_indexer
        MockedWriter.return_value = mock_writer

        mock_writer.write.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationMilvus()
        list(destination.write(self.config, configured_catalog, input_messages))

        MockedWriter.assert_called_once_with(self.config_model.processing, mock_indexer, mock_embedder, batch_size=128, omit_raw_text=False)
        mock_writer.write.assert_called_once_with(configured_catalog, input_messages)

    def test_spec(self):
        destination = DestinationMilvus()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)
