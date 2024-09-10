#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from airbyte_cdk.models import ConnectorSpecification, Status
from destination_qdrant.config import ConfigModel
from destination_qdrant.destination import DestinationQdrant


class TestDestinationQdrant(unittest.TestCase):
    def setUp(self):
        self.config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {
                "url": "localhost:6333",
                "auth_method": {
                    "mode": "no_auth",
                },
                "prefer_grpc": False,
                "collection": "dummy-collection",
                "distance_metric": "dot",
                "text_field": "text",
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = logging.getLogger("airbyte")

    @patch("destination_qdrant.destination.QdrantIndexer")
    @patch("destination_qdrant.destination.create_from_config")
    def test_check(self, MockedEmbedder, MockedQdrantIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        MockedQdrantIndexer.return_value = mock_indexer

        mock_embedder.check.return_value = None
        mock_indexer.check.return_value = None

        destination = DestinationQdrant()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_qdrant.destination.QdrantIndexer")
    @patch("destination_qdrant.destination.create_from_config")
    def test_check_with_errors(self, MockedEmbedder, MockedQdrantIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        MockedQdrantIndexer.return_value = mock_indexer

        embedder_error_message = "Embedder Error"
        indexer_error_message = "Indexer Error"

        mock_embedder.check.return_value = embedder_error_message
        mock_indexer.check.return_value = indexer_error_message

        destination = DestinationQdrant()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.FAILED)
        self.assertEqual(result.message, f"{embedder_error_message}\n{indexer_error_message}")

        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_qdrant.destination.Writer")
    @patch("destination_qdrant.destination.QdrantIndexer")
    @patch("destination_qdrant.destination.create_from_config")
    def test_write(self, MockedEmbedder, MockedQdrantIndexer, MockedWriter):
        mock_embedder = Mock()
        mock_indexer = Mock()
        mock_writer = Mock()

        MockedEmbedder.return_value = mock_embedder
        MockedQdrantIndexer.return_value = mock_indexer
        MockedWriter.return_value = mock_writer

        mock_writer.write.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationQdrant()
        list(destination.write(self.config, configured_catalog, input_messages))

        MockedWriter.assert_called_once_with(self.config_model.processing, mock_indexer, mock_embedder, batch_size=256, omit_raw_text=False)
        mock_writer.write.assert_called_once_with(configured_catalog, input_messages)

    def test_spec(self):
        destination = DestinationQdrant()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)
