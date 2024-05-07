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
                "account": "MYACCOUNT",
                "username": "MYUSERNAME",
                "password": "xxxxxxx",
                "database": "MYDATABASE",
                "warehouse": "MYWAREHOUSE",
                "role": "ACCOUNTADMIN"
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = AirbyteLogger()

    def test_spec(self):
        destination = DestinationSnowflakeCortex()
        result = destination.spec()

        self.assertIsInstance(result, ConnectorSpecification)
