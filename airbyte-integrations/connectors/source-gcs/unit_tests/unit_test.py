#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from io import BytesIO

import pandas as pd
from source_gcs.helpers import construct_file_schema


class TestGCSFunctions(unittest.TestCase):

    def setUp(self):
        # Initialize the mock config
        self.config = {
            'service_account': '{"test_key": "test_value"}',
            'gcs_bucket': 'test_bucket',
            'gcs_path': 'test_path'
        }

    def test_construct_file_schema(self):
        # Test that the function correctly constructs a JSON schema for a DataFrame
        df = pd.read_csv(BytesIO(b"id,name\n1,Alice\n2,Bob\n3,Charlie\n"))
        schema = construct_file_schema(df)
        expected_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"}
            }
        }
        self.assertEqual(schema, expected_schema)
