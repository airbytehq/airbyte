#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from io import BytesIO
from unittest.mock import MagicMock

import pandas as pd
from google.cloud.storage.blob import Blob
from source_gcs.helpers import construct_file_schema, read_csv_file


class TestGCSFunctions(unittest.TestCase):

    def setUp(self):
        # Initialize the mock config
        self.config = {
            'service_account': '{"test_key": "test_value"}',
            'gcs_bucket': 'test_bucket',
            'gcs_path': 'test_path'
        }

        # Initialize the mock Blob object
        self.blob = MagicMock(spec=Blob)
        self.blob.download_as_bytes.return_value = b"id,name\n1,Alice\n2,Bob\n3,Charlie\n"

    def test_read_csv_file(self):
        # Test that the function correctly reads a CSV file from a Blob object
        df = read_csv_file(self.blob)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertEqual(len(df), 3)
        self.assertEqual(list(df.columns), ['id', 'name'])

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
