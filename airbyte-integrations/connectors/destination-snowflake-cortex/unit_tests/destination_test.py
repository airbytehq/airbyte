#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from airbyte.strategies import WriteStrategy
from airbyte_cdk.models import ConnectorSpecification, Status

from destination_snowflake_cortex.config import ConfigModel
from destination_snowflake_cortex.destination import DestinationSnowflakeCortex


class TestDestinationSnowflakeCortex(unittest.TestCase):
    def setUp(self):
        self.config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {
                "host": "MYACCOUNT",
                "role": "MYUSERNAME",
                "warehouse": "MYWAREHOUSE",
                "database": "MYDATABASE",
                "default_schema": "MYSCHEMA",
                "username": "MYUSERNAME",
                "credentials": {"password": "xxxxxxx"},
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = logging.getLogger("airbyte")

    def test_spec(self):
        destination = DestinationSnowflakeCortex()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)

    @patch("destination_snowflake_cortex.cortex_processor.SnowflakeCortexSqlProcessor")
    def test_check(self, MockedSnowflakeCortexSqlProcessor):
        mock_processor = Mock()
        MockedSnowflakeCortexSqlProcessor.return_value = mock_processor

        destination = DestinationSnowflakeCortex()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_processor.sql_config.connect.assert_called_once()

    @patch("destination_snowflake_cortex.cortex_processor.SnowflakeCortexSqlProcessor")
    def test_check_with_errors(self, MockedSnowflakeCortexSqlProcessor):
        mock_processor = Mock()
        MockedSnowflakeCortexSqlProcessor.return_value = mock_processor

        indexer_error_message = "Indexer Error"
        mock_processor.sql_config.connect.side_effect = Exception(indexer_error_message)

        destination = DestinationSnowflakeCortex()
        result = destination.check(self.logger, self.config)
        self.assertEqual(result.status, Status.FAILED)
        mock_processor.sql_config.connect.assert_called_once()

    @patch("destination_snowflake_cortex.cortex_processor.SnowflakeCortexSqlProcessor")
    def test_write(
        self,
        MockedSnowflakeCortexProcessor,
    ):
        mock_processor = Mock()
        MockedSnowflakeCortexProcessor.return_value = mock_processor
        mock_processor.process_airbyte_messages_as_generator.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationSnowflakeCortex()
        list(destination.write(self.config, configured_catalog, input_messages))

        mock_processor.process_airbyte_messages_as_generator.assert_called_once_with(
            messages=input_messages,
            write_strategy=WriteStrategy.AUTO,
        )
