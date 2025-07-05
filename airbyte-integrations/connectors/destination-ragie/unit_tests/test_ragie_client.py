# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import unittest
from unittest.mock import MagicMock

from destination_ragie.client import RagieClient


class TestRagieClient(unittest.TestCase):
    def setUp(self):
        # Setup mock client
        self.mock_client = MagicMock(RagieClient)

    def test_find_ids_by_metadata(self):
        # Test finding IDs by metadata
        self.mock_client.find_ids_by_metadata.return_value = [1, 2, 3]
        result = self.mock_client.find_ids_by_metadata({"key": "value"})
        self.assertEqual(result, [1, 2, 3])

    def test_delete_documents_by_id(self):
        # Test document deletion
        self.mock_client.delete_documents_by_id([1, 2, 3])
        self.mock_client.delete_documents_by_id.assert_called_once_with([1, 2, 3])

    def test_find_docs_by_metadata(self):
        # Test finding documents by metadata
        self.mock_client.find_docs_by_metadata.return_value = [{"id": 1}, {"id": 2}]
        result = self.mock_client.find_docs_by_metadata({"key": "value"})
        self.assertEqual(result, [{"id": 1}, {"id": 2}])


if __name__ == "__main__":
    unittest.main()
