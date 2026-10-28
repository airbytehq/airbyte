# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
import unittest
from unittest.mock import MagicMock

from destination_ragie.client import RagieClient
from destination_ragie.config import RagieConfig


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


def test_request_does_not_log_authorization(requests_mock, caplog):
    client = RagieClient(RagieConfig(api_key="test-secret-not-for-logs"))
    requests_mock.get("https://api.ragie.ai/documents", json={"documents": []})

    with caplog.at_level(logging.DEBUG, logger="airbyte.destination_ragie.client"):
        response = client._request("GET", "/documents")

    assert response.status_code == 200
    assert requests_mock.last_request.headers["Authorization"] == "Bearer test-secret-not-for-logs"
    assert "Making GET request" in caplog.text
    assert "test-secret-not-for-logs" not in caplog.text
    assert "Authorization" not in caplog.text


if __name__ == "__main__":
    unittest.main()
