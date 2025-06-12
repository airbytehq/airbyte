#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from destination_pinecone.config import ConfigModel
from destination_pinecone.destination import DestinationPinecone

from airbyte_cdk.models import ConnectorSpecification, Status


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
        self.logger = logging.getLogger("airbyte")

    @patch("destination_pinecone.destination.PineconeIndexer")
    @patch("destination_pinecone.destination.create_from_config")
    def test_check(self, MockedEmbedder, MockedPineconeIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        MockedPineconeIndexer.return_value = mock_indexer

        mock_embedder.check.return_value = None
        mock_indexer.check.return_value = None

        destination = DestinationPinecone()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_pinecone.destination.PineconeIndexer")
    @patch("destination_pinecone.destination.create_from_config")
    def test_check_with_errors(self, MockedEmbedder, MockedPineconeIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
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

    def test_check_with_config_errors(self):
        bad_config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding_2": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {
                "pinecone_key": "mykey",
                "pinecone_environment": "myenv",
                "index": "myindex",
            },
        }
        destination = DestinationPinecone()
        result = destination.check(self.logger, bad_config)
        self.assertEqual(result.status, Status.FAILED)

    def test_check_with_init_indexer_errors(self):
        destination = DestinationPinecone()
        with patch("destination_pinecone.destination.PineconeIndexer", side_effect=Exception("Indexer Error")):
            result = destination.check(self.logger, self.config)
        self.assertEqual(result.status, Status.FAILED)

    @patch("destination_pinecone.destination.Writer")
    @patch("destination_pinecone.destination.PineconeIndexer")
    @patch("destination_pinecone.destination.create_from_config")
    def test_write(self, MockedEmbedder, MockedPineconeIndexer, MockedWriter):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        mock_writer = Mock()

        MockedPineconeIndexer.return_value = mock_indexer
        MockedWriter.return_value = mock_writer

        mock_writer.write.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationPinecone()
        list(destination.write(self.config, configured_catalog, input_messages))

        MockedWriter.assert_called_once_with(self.config_model.processing, mock_indexer, mock_embedder, batch_size=32, omit_raw_text=False)
        mock_writer.write.assert_called_once_with(configured_catalog, input_messages)

    def test_spec(self):
        destination = DestinationPinecone()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)
