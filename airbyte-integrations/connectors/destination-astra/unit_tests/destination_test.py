#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from airbyte_cdk.models import ConnectorSpecification, Status
from destination_astra.config import ConfigModel
from destination_astra.destination import DestinationAstra


class TestDestinationAstra(unittest.TestCase):
    def setUp(self):
        self.config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {
                "astra_db_app_token": "mytoken",
                "astra_db_endpoint": "https://8292d414-dd1b-4c33-8431-e838bedc04f7-us-east1.apps.astra.datastax.com",
                "astra_db_keyspace": "mykeyspace",
                "collection": "mycollection",
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = logging.getLogger("airbyte")

    @patch("destination_astra.destination.AstraIndexer")
    @patch("destination_astra.destination.create_from_config")
    def test_check(self, MockedEmbedder, MockedAstraIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        MockedAstraIndexer.return_value = mock_indexer

        mock_embedder.check.return_value = None
        mock_indexer.check.return_value = None

        destination = DestinationAstra()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_astra.destination.AstraIndexer")
    @patch("destination_astra.destination.create_from_config")
    def test_check_with_errors(self, MockedEmbedder, MockedAstraIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        MockedAstraIndexer.return_value = mock_indexer

        embedder_error_message = "Embedder Error"
        indexer_error_message = "Indexer Error"

        mock_embedder.check.return_value = embedder_error_message
        mock_indexer.check.return_value = indexer_error_message

        destination = DestinationAstra()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.FAILED)
        self.assertEqual(result.message, f"{embedder_error_message}\n{indexer_error_message}")

        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_astra.destination.Writer")
    @patch("destination_astra.destination.AstraIndexer")
    @patch("destination_astra.destination.create_from_config")
    def test_write(self, MockedEmbedder, MockedAstraIndexer, MockedWriter):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        mock_writer = Mock()

        MockedAstraIndexer.return_value = mock_indexer
        MockedWriter.return_value = mock_writer

        mock_writer.write.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationAstra()
        list(destination.write(self.config, configured_catalog, input_messages))

        MockedWriter.assert_called_once_with(self.config_model.processing, mock_indexer, mock_embedder, batch_size=100, omit_raw_text=False)
        mock_writer.write.assert_called_once_with(configured_catalog, input_messages)

    def test_spec(self):
        destination = DestinationAstra()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)
