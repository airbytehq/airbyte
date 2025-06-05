from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_ragie_client():
    """
    Automatically mock RagieClient across all tests.
    This prevents real HTTP calls during CI runs.
    """
    with patch("destination_ragie.destination.RagieClient") as mock_client_class:
        mock_client_instance = MagicMock()

        # Simulate mocked methods
        mock_client_instance.find_docs_by_metadata.return_value = [
            {"id": "doc1", "name": "Test Document", "metadata": {"external_id": "test_123"}}
        ]
        mock_client_instance.find_ids_by_metadata.return_value = ["doc1"]
        mock_client_instance.delete_documents_by_id.return_value = None

        # Patch instantiation
        mock_client_class.return_value = mock_client_instance
        yield mock_client_instance
