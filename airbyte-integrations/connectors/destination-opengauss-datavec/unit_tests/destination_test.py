#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from airbyte.strategies import WriteStrategy
from airbyte_cdk.models import ConnectorSpecification, Status

from destination_opengauss_datavec.config import ConfigModel
from destination_opengauss_datavec.destination import DestinationOpenGaussDataVec


class TestDestinationOpenGaussDataVec(unittest.TestCase):
    def setUp(self):
        self.config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {
                "host": "MYACCOUNT",
                "database": "MYDATABASE",
                "username": "MYUSERNAME",
                "password": "MYPASSWORD",
                "port": 5432,
                "default_schema": "MYSCHEMA",
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = logging.getLogger("airbyte")

    def test_spec(self):
        destination = DestinationOpenGaussDataVec()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)

    @patch("destination_opengauss_datavec.opengauss_processor.OpenGaussDataVecProcessor")
    def test_check(self, MockedOpenGaussDataVecProcessor):
        mock_processor = Mock()
        MockedOpenGaussDataVecProcessor.return_value = mock_processor

        destination = DestinationOpenGaussDataVec()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_processor.sql_config.get_sql_engine().connect.assert_called_once()

    @patch("destination_opengauss_datavec.opengauss_processor.OpenGaussDataVecProcessor")
    def test_check_with_errors(self, MockedOpenGaussDataVecProcessor):
        mock_processor = Mock()
        MockedOpenGaussDataVecProcessor.return_value = mock_processor

        indexer_error_message = "Indexer Error"
        mock_processor.sql_config.get_sql_engine().connect.side_effect = Exception(
            indexer_error_message
        )

        destination = DestinationOpenGaussDataVec()
        result = destination.check(self.logger, self.config)
        self.assertEqual(result.status, Status.FAILED)
        mock_processor.sql_config.get_sql_engine().connect.assert_called_once()

    @patch("destination_opengauss_datavec.opengauss_processor.OpenGaussDataVecProcessor")
    def test_write(
        self,
        MockedOpenGaussDataVecProcessor,
    ):
        mock_processor = Mock()
        MockedOpenGaussDataVecProcessor.return_value = mock_processor
        mock_processor.process_airbyte_messages_as_generator.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationOpenGaussDataVec()
        list(destination.write(self.config, configured_catalog, input_messages))

        mock_processor.process_airbyte_messages_as_generator.assert_called_once_with(
            messages=input_messages,
            write_strategy=WriteStrategy.AUTO,
        )
