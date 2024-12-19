#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from airbyte_cdk.models import ConnectorSpecification, Status
from destination_weaviate.config import ConfigModel
from destination_weaviate.destination import DestinationWeaviate


class TestDestinationWeaviate(unittest.TestCase):
    def setUp(self):
        self.config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {"host": "https://my-cluster.weaviate.network", "auth": {"mode": "no_auth"}},
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = logging.getLogger("airbyte")

    @patch("destination_weaviate.destination.WeaviateIndexer")
    @patch("destination_weaviate.destination.create_from_config")
    def test_check(self, MockedEmbedder, MockedWeaviateIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        MockedWeaviateIndexer.return_value = mock_indexer

        mock_embedder.check.return_value = None
        mock_indexer.check.return_value = None

        destination = DestinationWeaviate()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_weaviate.destination.WeaviateIndexer")
    @patch("destination_weaviate.destination.create_from_config")
    def test_check_with_errors(self, MockedEmbedder, MockedWeaviateIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        MockedWeaviateIndexer.return_value = mock_indexer

        embedder_error_message = "Embedder Error"
        indexer_error_message = "Indexer Error"

        mock_embedder.check.return_value = embedder_error_message
        mock_indexer.check.return_value = indexer_error_message

        destination = DestinationWeaviate()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.FAILED)
        self.assertEqual(result.message, f"{embedder_error_message}\n{indexer_error_message}")

        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_weaviate.destination.Writer")
    @patch("destination_weaviate.destination.WeaviateIndexer")
    @patch("destination_weaviate.destination.create_from_config")
    def test_write(self, MockedEmbedder, MockedWeaviateIndexer, MockedWriter):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        mock_writer = Mock()

        MockedWeaviateIndexer.return_value = mock_indexer
        MockedWriter.return_value = mock_writer

        mock_writer.write.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationWeaviate()
        list(destination.write(self.config, configured_catalog, input_messages))

        MockedWriter.assert_called_once_with(self.config_model.processing, mock_indexer, mock_embedder, batch_size=128, omit_raw_text=False)
        mock_writer.write.assert_called_once_with(configured_catalog, input_messages)

    def test_spec(self):
        destination = DestinationWeaviate()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)
