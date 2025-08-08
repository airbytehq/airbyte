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
    mock_file_1.path = "airbyte-integrations/connectors/source-test-1/metadata.yaml"
    mock_file_1.download_url = "https://github.com/connector-1/metadata.yaml"

    mock_file_2 = Mock()
    mock_file_2.type = "file"
    mock_file_2.name = "metadata.yaml"
    mock_file_2.path = "airbyte-integrations/connectors/source-test-2/metadata.yaml"
    mock_file_2.download_url = "https://github.com/connector-2/metadata.yaml"

    mock_file_3 = Mock()
    mock_file_3.type = "file"
    mock_file_3.name = "metadata.yaml"
    mock_file_3.path = "airbyte-integrations/connectors/source-test-3/metadata.yaml"
    mock_file_3.download_url = "https://github.com/connector-3/metadata.yaml"

    return [mock_file_1, mock_file_2, mock_file_3]


@pytest.fixture
def mock_yaml_responses():
    """Create mock YAML responses for different test scenarios."""
    return {
        "https://github.com/connector-1/metadata.yaml": """
metadataSpecVersion: "1.0"
data:
    name: "Test Source 1"
    definitionId: "12345678-1234-1234-1234-123456789abc"
    connectorType: "source"
    dockerRepository: "airbyte/source-test-1"
    dockerImageTag: "1.0.0"
    license: "MIT"
    documentationUrl: "https://docs.airbyte.com/integrations/sources/test-1"
    githubIssueLabel: "source-test-1"
    connectorSubtype: "api"
    releaseStage: "alpha"
    supportLevel: "certified"
""",
        "https://github.com/connector-2/metadata.yaml": """
metadataSpecVersion: "1.0"
data:
    name: "Test Source 2"
    definitionId: "12345678-1234-1234-1234-123456789abd"
    connectorType: "source"
    dockerRepository: "airbyte/source-test-2"
    dockerImageTag: "1.0.0-rc"
    license: "MIT"
    documentationUrl: "https://docs.airbyte.com/integrations/sources/test-2"
    githubIssueLabel: "source-test-2"
    connectorSubtype: "api"
    releaseStage: "alpha"
    supportLevel: "community"
""",
        "https://github.com/connector-3/metadata.yaml": """
metadataSpecVersion: "1.0"
data:
    name: "Test Source 3"
    definitionId: "12345678-1234-1234-1234-123456789abe"
    connectorType: "source"
    dockerRepository: "airbyte/source-test-3"
    dockerImageTag: "2.0.0"
    license: "MIT"
    documentationUrl: "https://docs.airbyte.com/integrations/sources/test-3"
    githubIssueLabel: "source-test-3"
    connectorSubtype: "api"
    releaseStage: "alpha"
    supportLevel: "archived"
""",
    }


@pytest.fixture
def mock_gcs_blobs():
    """Create mock GCS blob objects for testing."""

    def _create_mock_blob(repo, tag):
        blob = Mock()
        metadata = {
            "metadataSpecVersion": "1.0",
            "data": {
                "name": f"Test {repo.split('/')[-1].replace('-', ' ').title()}",
                "definitionId": "12345678-1234-1234-1234-123456789000",
                "connectorType": "source" if "source" in repo else "destination",
                "dockerRepository": repo,
                "dockerImageTag": tag,
                "license": "MIT",
                "documentationUrl": f"https://docs.airbyte.com/integrations/{repo}",
                "githubIssueLabel": repo.split("/")[-1],
                "connectorSubtype": "api",
                "releaseStage": "alpha",
                "supportLevel": "certified",
            },
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
