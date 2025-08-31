#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from destination_opengauss_datavec.config import ConfigModel
from destination_opengauss_datavec.destination import DestinationOpenGaussDataVec

from airbyte_cdk.models import ConnectorSpecification, Status


class TestDestinationOpenGaussDataVec(unittest.TestCase):
    def setUp(self):
        self.config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "fake"},
            "indexing": {
                "host": "localhost",
                "database": "postgres",
                "username": "hly",
                "password": "Hly12345",
                "port": 8888,
                "schema": "public",
                "default_schema": "public",
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        # 配置日志输出到控制台，好像没起作用
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("airbyte")
        # 确保日志输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)

    @patch("destination_opengauss_datavec.destination.OpenGaussDataVecIndexer")
    @patch("destination_opengauss_datavec.destination.create_from_config")
    def test_check(self, MockedEmbedder, MockedOpenGaussDataVecIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        MockedOpenGaussDataVecIndexer.return_value = mock_indexer

        mock_embedder.check.return_value = None
        mock_indexer.check.return_value = None

        destination = DestinationOpenGaussDataVec()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_opengauss_datavec.destination.OpenGaussDataVecIndexer")
    @patch("destination_opengauss_datavec.destination.create_from_config")
    def test_check_with_errors(self, MockedEmbedder, MockedOpenGaussDataVecIndexer):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        MockedOpenGaussDataVecIndexer.return_value = mock_indexer

        embedder_error_message = "Embedder Error"
        indexer_error_message = "Indexer Error"

        mock_embedder.check.return_value = embedder_error_message
        mock_indexer.check.return_value = indexer_error_message

        destination = DestinationOpenGaussDataVec()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.FAILED)
        self.assertEqual(result.message, f"{embedder_error_message}\n{indexer_error_message}")

        mock_embedder.check.assert_called_once()
        mock_indexer.check.assert_called_once()

    @patch("destination_opengauss_datavec.destination.Writer")
    @patch("destination_opengauss_datavec.destination.OpenGaussDataVecIndexer")
    @patch("destination_opengauss_datavec.destination.create_from_config")
    def test_write(self, MockedEmbedder, MockedOpenGaussDataVecIndexer, MockedWriter):
        mock_embedder = Mock()
        mock_indexer = Mock()
        mock_writer = Mock()

        MockedEmbedder.return_value = mock_embedder
        MockedOpenGaussDataVecIndexer.return_value = mock_indexer
        MockedWriter.return_value = mock_writer

        mock_writer.write.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationOpenGaussDataVec()
        list(destination.write(self.config, configured_catalog, input_messages))

        MockedWriter.assert_called_once_with(self.config_model.processing, mock_indexer, mock_embedder, batch_size=128, omit_raw_text=False)
        mock_writer.write.assert_called_once_with(configured_catalog, input_messages)

    def test_spec(self):
        destination = DestinationOpenGaussDataVec()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)
