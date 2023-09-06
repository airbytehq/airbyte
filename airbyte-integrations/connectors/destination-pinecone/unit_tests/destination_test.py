#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock, Mock, patch

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification, Status
from destination_pinecone.config import ConfigModel
from destination_pinecone.destination import DestinationPinecone, embedder_map


class TestDestinationPinecone(unittest.TestCase):
    def setUp(self):
        self.config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {
                "pinecone_key": "mykey",
                "pinecone_environment": "myenv",
                "index": "myindex",
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = AirbyteLogger()

    @patch("destination_pinecone.destination.PineconeIndexer")
    @patch.dict(embedder_map, openai=MagicMock())
    def test_check(self, MockedPineconeIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        embedder_map["openai"].return_value = mock_embedder
        MockedPineconeIndexer.return_value = mock_indexer

        mock_embedder.check.return_value = None
        mock_indexer.check.return_value = None

        destination = DestinationPinecone()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_pinecone.destination.PineconeIndexer")
    @patch.dict(embedder_map, openai=MagicMock())
    def test_check_with_errors(self, MockedPineconeIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        embedder_map["openai"].return_value = mock_embedder
        MockedPineconeIndexer.return_value = mock_indexer

        embedder_error_message = "Embedder Error"
        indexer_error_message = "Indexer Error"

        mock_embedder.check.return_value = embedder_error_message
        mock_indexer.check.return_value = indexer_error_message

        destination = DestinationPinecone()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.FAILED)
        self.assertEqual(result.message, f"{embedder_error_message}\n{indexer_error_message}")

        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_pinecone.destination.Writer")
    @patch("destination_pinecone.destination.PineconeIndexer")
    @patch.dict(embedder_map, openai=MagicMock())
    def test_write(self, MockedPineconeIndexer, MockedWriter):
        mock_embedder = Mock()
        mock_indexer = Mock()
        mock_writer = Mock()

        embedder_map["openai"].return_value = mock_embedder
        MockedPineconeIndexer.return_value = mock_indexer
        MockedWriter.return_value = mock_writer

        mock_writer.write.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationPinecone()
        list(destination.write(self.config, configured_catalog, input_messages))

        MockedWriter.assert_called_once_with(self.config_model.processing, mock_indexer, mock_embedder, batch_size=128)
        mock_writer.write.assert_called_once_with(configured_catalog, input_messages)

    def test_spec(self):
        destination = DestinationPinecone()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)
