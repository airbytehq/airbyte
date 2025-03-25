#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from airbyte.strategies import WriteStrategy
from airbyte_cdk.models import ConnectorSpecification, Status

from destination_mariadb.config import ConfigModel
from destination_mariadb.destination import DestinationMariaDB


class TestDestinationMariaDB(unittest.TestCase):
    def setUp(self):
        self.config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {
                "host": "MYACCOUNT",
                "port": 5432,
                "database": "MYDATABASE",
                "default_schema": "MYSCHEMA",
                "username": "MYUSERNAME",
                "credentials": {"password": "xxxxxxx"},
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = logging.getLogger("airbyte")

    def test_spec(self):
        destination = DestinationMariaDB()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)

    @patch("destination_mariadb.mariadb_processor.MariaDBProcessor")
    def test_check(self, MockedMariaDBProcessor):
        mock_processor = Mock()
        MockedMariaDBProcessor.return_value = mock_processor

        destination = DestinationMariaDB()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_processor.sql_config.connect.assert_called_once()

    @patch("destination_mariadb.mariadb_processor.MariaDBProcessor")
    def test_check_with_errors(self, MockedMariaDBProcessor):
        mock_processor = Mock()
        MockedMariaDBProcessor.return_value = mock_processor

        indexer_error_message = "Indexer Error"
        mock_processor.sql_config.connect.side_effect = Exception(indexer_error_message)

        destination = DestinationMariaDB()
        result = destination.check(self.logger, self.config)
        self.assertEqual(result.status, Status.FAILED)
        mock_processor.sql_config.connect.assert_called_once()

    @patch("destination_mariadb.mariadb_processor.MariaDBProcessor")
    def test_write(
        self,
        MockedMariaDBProcessor,
    ):
        mock_processor = Mock()
        MockedMariaDBProcessor.return_value = mock_processor
        mock_processor.process_airbyte_messages_as_generator.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationMariaDB()
        list(destination.write(self.config, configured_catalog, input_messages))

        mock_processor.process_airbyte_messages_as_generator.assert_called_once_with(
            messages=input_messages,
            write_strategy=WriteStrategy.AUTO,
        )
