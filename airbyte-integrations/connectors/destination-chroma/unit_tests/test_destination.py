#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from destination_chroma.config import ConfigModel
from destination_chroma.destination import DestinationChroma

from airbyte_cdk.models import ConnectorSpecification, Status


class TestDestinationChroma(unittest.TestCase):
    def setUp(self):
        self.config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {
                "auth_method": {"mode": "persistent_client", "path": "./path"},
                "collection_name": "test2",
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = logging.getLogger("airbyte")

    @patch("destination_chroma.destination.ChromaIndexer")
    @patch("destination_chroma.destination.create_from_config")
    def test_check(self, MockedEmbedder, MockedChromaIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedChromaIndexer.return_value = mock_indexer
        MockedEmbedder.return_value = mock_embedder

        mock_embedder.check.return_value = None
        mock_indexer.check.return_value = None

        destination = DestinationChroma()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_chroma.destination.ChromaIndexer")
    @patch("destination_chroma.destination.create_from_config")
    def test_check_with_errors(self, MockedEmbedder, MockedChromaIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedChromaIndexer.return_value = mock_indexer
        MockedEmbedder.return_value = mock_embedder

        embedder_error_message = "Embedder Error"
        indexer_error_message = "Indexer Error"

        mock_embedder.check.return_value = embedder_error_message
        mock_indexer.check.return_value = indexer_error_message

        destination = DestinationChroma()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.FAILED)
        self.assertEqual(result.message, f"{embedder_error_message}\n{indexer_error_message}")

        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_chroma.destination.Writer")
    @patch("destination_chroma.destination.ChromaIndexer")
    @patch("destination_chroma.destination.create_from_config")
    def test_write(self, MockedEmbedder, MockedChromaIndexer, MockedWriter):
        mock_embedder = Mock()
        mock_indexer = Mock()
        mock_writer = Mock()

        MockedChromaIndexer.return_value = mock_indexer
        MockedWriter.return_value = mock_writer
        MockedEmbedder.return_value = mock_embedder

        mock_writer.write.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationChroma()
        list(destination.write(self.config, configured_catalog, input_messages))

        MockedWriter.assert_called_once_with(self.config_model.processing, mock_indexer, mock_embedder, batch_size=128, omit_raw_text=False)
        mock_writer.write.assert_called_once_with(configured_catalog, input_messages)

    def test_spec(self):
        destination = DestinationChroma()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)
