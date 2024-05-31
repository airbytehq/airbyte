#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock, Mock, patch

from airbyte_cdk import AirbyteLogger
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
                    "credentials": {
                        "password": "xxxxxxx"
                    }
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = AirbyteLogger()

    def test_spec(self):
        destination = DestinationSnowflakeCortex()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)

    @patch("destination_snowflake_cortex.destination.SnowflakeCortexIndexer")
    def test_check(self, MockedSnowflakeCortexIndexer):
        mock_indexer = Mock()
        MockedSnowflakeCortexIndexer.return_value = mock_indexer

        destination = DestinationSnowflakeCortex()
        result = destination.check(self.logger, self.config)

        self.assertEqual(result.status, Status.SUCCEEDED)
        mock_indexer.check.assert_called_once()

    @patch("destination_snowflake_cortex.destination.SnowflakeCortexIndexer")
    def test_check_with_errors(self, MockedSnowflakeCortexIndexer):
        mock_indexer = Mock()
        MockedSnowflakeCortexIndexer.return_value = mock_indexer

        indexer_error_message = "Indexer Error"
        mock_indexer.check.side_effect = Exception(indexer_error_message)

        destination = DestinationSnowflakeCortex()
        result = destination.check(self.logger, self.config)
        self.assertEqual(result.status, Status.FAILED)
        mock_indexer.check.assert_called_once()

    @patch("destination_snowflake_cortex.destination.Writer")
    @patch("destination_snowflake_cortex.destination.SnowflakeCortexIndexer")
    @patch("destination_snowflake_cortex.destination.create_from_config")
    def test_write(self, MockedEmbedder, MockedSnowflakeCortexIndexer, MockedWriter):
        mock_embedder = Mock()
        mock_indexer = Mock()
        MockedEmbedder.return_value = mock_embedder
        mock_writer = Mock()

        MockedSnowflakeCortexIndexer.return_value = mock_indexer
        MockedWriter.return_value = mock_writer

        mock_writer.write.return_value = []

        configured_catalog = MagicMock()
        input_messages = []

        destination = DestinationSnowflakeCortex()
        list(destination.write(self.config, configured_catalog, input_messages))

        MockedWriter.assert_called_once_with(self.config_model.processing, mock_indexer, mock_embedder, batch_size=150, omit_raw_text=False)
        mock_writer.write.assert_called_once_with(configured_catalog, input_messages)
