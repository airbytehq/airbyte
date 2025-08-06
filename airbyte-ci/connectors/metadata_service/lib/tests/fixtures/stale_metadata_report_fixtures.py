#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
import yaml


@pytest.fixture
def mock_github_files():
    """Create mock GitHub file objects for testing."""
    mock_file_1 = Mock()
    mock_file_1.type = "file"
    mock_file_1.name = "metadata.yaml"
    mock_file_1.path = "some/random/path/metadata.yaml"
    mock_file_1.download_url = "https://github.com/connector-1/metadata.yaml"

    mock_file_2 = Mock()
    mock_file_2.type = "file"
    mock_file_2.name = "metadata.yaml"
    mock_file_2.path = "some/random/path2/metadata.yaml"
    mock_file_2.download_url = "https://github.com/connector-2/metadata.yaml"

    mock_file_3 = Mock()
    mock_file_3.type = "file"
    mock_file_3.name = "metadata.yaml"
    mock_file_3.path = "some/random/path3/metadata.yaml"
    mock_file_3.download_url = "https://github.com/connector-3/metadata.yaml"

    return [mock_file_1, mock_file_2, mock_file_3]


@pytest.fixture
def mock_yaml_responses():
    """Create mock YAML responses for different test scenarios."""
    return {
        "https://github.com/connector-1/metadata.yaml": """
data:
    dockerRepository: "airbyte/source-test-1"
    dockerImageTag: "1.0.0"
    supportLevel: "certified"
""",
        "https://github.com/connector-2/metadata.yaml": """
data:
    dockerRepository: "airbyte/source-test-2"
    dockerImageTag: "1.0.0-rc"
    supportLevel: "community"
""",
        "https://github.com/connector-3/metadata.yaml": """
data:
    dockerRepository: "airbyte/source-test-3"
    dockerImageTag: "2.0.0"
    supportLevel: "archived"
""",
    }


@pytest.fixture
def mock_gcs_blobs():
    """Create mock GCS blob objects for testing."""

    def _create_mock_blob(repo, tag):
        blob = Mock()
        metadata = {
            "data": {
                "dockerRepository": repo,
                "dockerImageTag": tag,
                "supportLevel": "certified",
            }
        }
        blob.download_as_bytes.return_value = yaml.dump(metadata).encode("utf-8")
        return blob

    mock_blob_1 = _create_mock_blob("airbyte/source-gcs-1", "1.2.0")
    mock_blob_2 = _create_mock_blob("airbyte/source-gcs-2", "2.1.0")
    mock_blob_3 = _create_mock_blob("airbyte/destination-gcs-1", "3.0.0")

    return [mock_blob_1, mock_blob_2, mock_blob_3]


@pytest.fixture
def large_dataset_github_mappings():
    """Create large GitHub version mappings for performance testing."""
    return {f"airbyte/connector-{i:04d}": f"{i % 10}.{i % 5}.{i % 3}" for i in range(500)}


@pytest.fixture
def large_dataset_gcs_mappings():
    """Create large GCS version mappings for performance testing."""
    return {f"airbyte/connector-{i:04d}": f"{(i - 1) % 10}.{i % 5}.{i % 3}" for i in range(500)}
