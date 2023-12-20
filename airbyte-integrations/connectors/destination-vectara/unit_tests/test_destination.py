#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock, Mock, patch

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification, Status
from destination_vectara.config import VectaraConfig
from destination_vectara.destination import DestinationVectara


class TestDestinationVectara(unittest.TestCase):
    def setUp(self):
        self.config = {
            "oauth2": {"client_id": "client_id", "client_secret": "client_secret"},
            "customer_id": "customer_id",
            "corpus_name": "corpus_name",
            "text_fields": ["field1", "field2"], 
            "metadata_fields": ["field3"], 
        }
        self.config_model = VectaraConfig.parse_obj(self.config)
        self.logger = AirbyteLogger()

    @patch("destination_vectara.destination.VectaraWriter")
    def test_check(self, MockedVectaraWriter):
        mock_writer = Mock()
        MockedVectaraWriter.return_value = mock_writer

        mock_writer.check.return_value = None

        destination = DestinationVectara()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_writer.check.assert_called_once()

    @patch("destination_vectara.destination.VectaraWriter")
    @patch("destination_vectara.destination.create_from_config")
    def test_check_with_errors(self, MockedVectaraWriter):
        mock_writer = Mock()
        MockedVectaraWriter.return_value = mock_writer

        indexer_error_message = "Indexer Error"

        mock_writer.check.return_value = indexer_error_message

        destination = DestinationVectara()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.FAILED)
        self.assertEqual(result.message, indexer_error_message)

        mock_writer.check.assert_called_once()

    @patch("destination_vectara.destination.Writer")
    @patch("destination_vectara.destination.VectaraWriter")
    @patch("destination_vectara.destination.create_from_config")
    def test_write(self, MockedVectaraWriter, MockedWriter):
        mock_writer = Mock()
        mock_writer = Mock()

        MockedVectaraWriter.return_value = mock_writer
        MockedWriter.return_value = mock_writer

        mock_writer.write.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationVectara()
        list(destination.write(self.config, configured_catalog, input_messages))

        MockedWriter.assert_called_once_with(self.config_model.processing, mock_writer, batch_size=128)
        mock_writer.write.assert_called_once_with(configured_catalog, input_messages)

    def test_spec(self):
        destination = DestinationVectara()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)
