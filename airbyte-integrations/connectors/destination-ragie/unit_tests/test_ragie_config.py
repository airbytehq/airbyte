# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
import unittest

from destination_ragie.config import RagieConfig
from pydantic import ValidationError


class TestRagieConfig(unittest.TestCase):
    def setUp(self):
        # Setup mock config
        # Example: Add the required field
        self.mock_config = RagieConfig(
            api_key="dummy_key",
            content_fields=["field1", "field2"],
            metadata_fields=["meta1", "meta2"],
            partition="test_partition",
            processing_mode="fast",
            document_name_field="doc_name",
        )

    def test_content_fields(self):
        self.assertEqual(self.mock_config.content_fields, ["field1", "field2"])

    def test_metadata_fields(self):
        self.assertEqual(self.mock_config.metadata_fields, ["meta1", "meta2"])

    def test_partition(self):
        self.assertEqual(self.mock_config.partition, "test_partition")

    def test_processing_mode(self):
        self.assertEqual(self.mock_config.processing_mode, "fast")

    def test_document_name_field(self):
        self.assertEqual(self.mock_config.document_name_field, "doc_name")

    def test_api_key(self):
        self.assertEqual(self.mock_config.api_key, "dummy_key")

    def test_default_metadata_static(self):
        self.assertEqual(self.mock_config.metadata_static, "")

    def test_default_external_id_field(self):
        self.assertEqual(self.mock_config.external_id_field, "")

    def test_metadata_static_dict_empty(self):
        self.assertEqual(self.mock_config.metadata_static_dict, {})

    def test_metadata_static_dict_with_value(self):
        config = RagieConfig(api_key="key", metadata_static='{"source": "airbyte", "env": "test"}')
        expected = {"source": "airbyte", "env": "test"}
        self.assertEqual(config.metadata_static_dict, expected)

    def test_metadata_static_validator_valid(self):
        valid_json = '{"key": "value"}'
        config = RagieConfig(api_key="key", metadata_static=valid_json)
        self.assertEqual(config.metadata_static, valid_json)

    def test_metadata_static_validator_invalid(self):
        invalid_json = "not a json"
        with self.assertRaises(ValidationError):
            RagieConfig(api_key="key", metadata_static=invalid_json)

    def test_metadata_static_validator_not_object(self):
        array_json = "[1, 2, 3]"
        with self.assertRaises(ValidationError):
            RagieConfig(api_key="key", metadata_static=array_json)


if __name__ == "__main__":
    unittest.main()

if __name__ == "__main__":
    unittest.main()
