#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import os
import pathlib
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest
import yaml

from metadata_service.registry_entry import generate_and_persist_registry_entry


@pytest.fixture
def sample_spec_dict():
    """Sample spec dictionary for testing."""
    return {
        "documentationUrl": "https://docs.airbyte.com/integrations/sources/test",
        "connectionSpecification": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Test Source Spec",
            "type": "object",
            "properties": {"api_key": {"type": "string", "title": "API Key", "description": "API key for authentication"}},
            "required": ["api_key"],
        },
    }


@pytest.fixture
def sample_dependencies_dict():
    """Sample dependencies dictionary for testing."""
    return {"dependencies": [{"package_name": "airbyte-cdk", "version": "0.50.0"}, {"package_name": "requests", "version": "2.28.0"}]}


@pytest.fixture(
    params=[
        # (registry_type, enabled, version_type)
        ("oss", True, "latest"),
        ("cloud", True, "latest"),
        ("oss", True, "rc"),
        ("cloud", True, "rc"),
        ("oss", True, "dev"),
        ("cloud", True, "dev"),
        ("oss", False, "latest"),
        ("cloud", False, "latest"),
        ("oss", False, "rc"),
        ("cloud", False, "rc"),
        ("oss", False, "dev"),
        ("cloud", False, "dev"),
    ]
)
def registry_scenario(request, sample_spec_dict):
    """Parameterized fixture providing different registry scenarios with temp files."""
    registry_type, enabled, version_type = request.param

    # Create metadata dict based on enabled/disabled status
    docker_tag = "1.0.0"
    if version_type == "rc":
        docker_tag = "1.0.0-rc"
    elif version_type == "dev":
        docker_tag = "1.0.0-dev"

    metadata_dict = {
        "metadataSpecVersion": "1.0",
        "data": {
            "name": f"Test Source {'Enabled' if enabled else 'Disabled'}",
            "definitionId": "12345678-1234-1234-1234-123456789012",
            "connectorType": "source",
            "dockerRepository": f"airbyte/source-test-{'enabled' if enabled else 'disabled'}",
            "dockerImageTag": docker_tag,
            "documentationUrl": f"https://docs.airbyte.com/integrations/sources/test-{'enabled' if enabled else 'disabled'}",
            "connectorSubtype": "api",
            "releaseStage": "beta",
            "license": "MIT",
            "registryOverrides": {"oss": {"enabled": enabled}, "cloud": {"enabled": enabled}},
            "tags": ["language:python"],
        },
    }

    # Create temporary files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create metadata file
        metadata_path = pathlib.Path(temp_dir) / "metadata.yaml"
        with open(metadata_path, "w") as f:
            yaml.dump(metadata_dict, f)

        # Create spec file
        spec_path = pathlib.Path(temp_dir) / "spec.json"
        with open(spec_path, "w") as f:
            json.dump(sample_spec_dict, f)

        yield {
            "registry_type": registry_type,
            "enabled": enabled,
            "version_type": version_type,
            "metadata_path": metadata_path,
            "spec_path": spec_path,
            "metadata_dict": metadata_dict,
            "docker_image_tag": docker_tag,
            "is_prerelease": version_type == "dev",
        }


@patch("metadata_service.registry_entry.send_slack_message")
@patch("metadata_service.registry_entry._persist_connector_registry_entry")
@patch("metadata_service.registry_entry._get_icon_blob_from_gcs")
@patch("metadata_service.registry_entry.safe_read_gcs_file")
@patch("metadata_service.registry_entry.get_gcs_storage_client")
@patch("metadata_service.registry.storage.Client")
@patch("metadata_service.registry_entry.SpecCache")
def test_generate_and_persist_registry_entry(
    mock_spec_cache_class,
    mock_storage_client_class,
    mock_gcs_client,
    mock_safe_read_gcs_file,
    mock_get_icon_blob,
    mock_persist_entry,
    mock_send_slack,
    registry_scenario,
    sample_dependencies_dict,
):
    """Test registry entry generation for all scenarios: enabled/disabled, all registry types, and all version types."""
    # Arrange
    scenario = registry_scenario
    bucket_name = "test-bucket"

    # Mock GCS client setup
    mock_storage_client = Mock()
    mock_storage_client_class.return_value = mock_storage_client
    mock_bucket = Mock()
    mock_blob = Mock()
    mock_icon_blob = Mock()

    mock_gcs_client.return_value = mock_storage_client
    mock_storage_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_bucket.delete_blob = Mock()

    mock_spec_cache = Mock()
    mock_spec_cache_class.return_value = mock_spec_cache
    mock_spec_cache.download_spec.return_value = json.loads('{"fake": "spec"}')

    mock_blob.download_as_string.return_value = yaml.dump(scenario["metadata_dict"])
    mock_blob.name = "fake/blob/path.yaml"
    mock_blob.updated.isoformat.return_value = "2025-01-23T12:34:56Z"

    if scenario["enabled"]:
        # Mock successful operations for enabled scenarios
        mock_safe_read_gcs_file.return_value = json.dumps(sample_dependencies_dict)
        mock_icon_blob.bucket.name = bucket_name
        mock_icon_blob.name = f"metadata/{scenario['metadata_dict']['data']['dockerRepository']}/latest/icon.svg"
        mock_get_icon_blob.return_value = mock_icon_blob
    else:
        # Mock existing blob for deletion scenarios (latest versions only)
        mock_blob.exists.return_value = True

    # Act
    generate_and_persist_registry_entry(
        bucket_name=bucket_name,
        repo_metadata_file_path=scenario["metadata_path"],
        registry_type=scenario["registry_type"],
        docker_image_tag=scenario["docker_image_tag"],
        is_prerelease=scenario["is_prerelease"],
    )

    # Assert based on enabled/disabled status
    if scenario["enabled"]:
        # ENABLED SCENARIO ASSERTIONS

        # Verify GCS operations were called
        mock_gcs_client.assert_called()
        mock_safe_read_gcs_file.assert_called_once()
        mock_get_icon_blob.assert_called_once_with(bucket_name, scenario["metadata_dict"]["data"])

        # Verify registry entry was persisted
        mock_persist_entry.assert_called()
        persist_call_args = mock_persist_entry.call_args_list

        # Check number of persist calls based on version type
        if scenario["version_type"] == "latest" or scenario["version_type"] == "rc":
            # in "latest" mode, we write to versioned + `/latest`
            # in "rc" mode, we write to versioned + `/release_candidate`
            assert len(persist_call_args) == 2
        else:  # dev
            assert len(persist_call_args) == 1  # only one path

        # Verify the registry entry model was created correctly
        for call_args in persist_call_args:
            bucket_name_arg, registry_entry_model, registry_path = call_args[0]
            assert bucket_name_arg == bucket_name
            assert scenario["registry_type"] in registry_path

            # Verify the model has expected fields
            registry_entry_dict = json.loads(registry_entry_model.json(exclude_none=True))

            # Check core field transformations
            assert "sourceDefinitionId" in registry_entry_dict
            assert registry_entry_dict["sourceDefinitionId"] == scenario["metadata_dict"]["data"]["definitionId"]

            # Verify required fields were added
            assert registry_entry_dict["tombstone"] is False
            assert registry_entry_dict["custom"] is False
            assert registry_entry_dict["public"] is True
            assert "iconUrl" in registry_entry_dict
            assert "generated" in registry_entry_dict
            assert "packageInfo" in registry_entry_dict
            assert registry_entry_dict["packageInfo"]["cdk_version"] == "python:0.50.0"
            assert "spec" in registry_entry_dict

            # Verify fields were removed
            assert "registryOverrides" not in registry_entry_dict
            assert "connectorType" not in registry_entry_dict
            assert "definitionId" not in registry_entry_dict

        registry_entry_paths = set()
        for kall in persist_call_args:
            args, _ = kall
            # blob path is the last positional arg
            registry_entry_paths.add(args[-1])
        if scenario["version_type"] == "rc":
            assert registry_entry_paths == {
                f'metadata/airbyte/source-test-enabled/{scenario["docker_image_tag"]}/{scenario["registry_type"]}.json',
                f'metadata/airbyte/source-test-enabled/release_candidate/{scenario["registry_type"]}.json',
            }
        elif scenario["version_type"] == "latest":
            assert registry_entry_paths == {
                f'metadata/airbyte/source-test-enabled/{scenario["docker_image_tag"]}/{scenario["registry_type"]}.json',
                f'metadata/airbyte/source-test-enabled/latest/{scenario["registry_type"]}.json',
            }
        elif scenario["version_type"] == "dev":
            assert registry_entry_paths == {
                f'metadata/airbyte/source-test-enabled/{scenario["docker_image_tag"]}/{scenario["registry_type"]}.json',
            }
        else:
            raise Exception(f'Unexpected scenario: {scenario["version_type"]}')

        # Verify Slack notifications
        slack_calls = mock_send_slack.call_args_list
        assert len(slack_calls) >= 2  # start + success notifications

        start_call = slack_calls[0][0]
        assert "Registry Entry Generation_ STARTED" in start_call[1]

        success_calls = [call for call in slack_calls if "SUCCESS" in call[0][1]]
        assert len(success_calls) == len(persist_call_args)

    else:
        # DISABLED SCENARIO ASSERTIONS

        # Verify NO generation/persistence operations were called
        mock_safe_read_gcs_file.assert_not_called()
        mock_get_icon_blob.assert_not_called()
        mock_persist_entry.assert_not_called()

        if scenario["version_type"] == "latest":
            # For latest versions, should check for deletion
            mock_gcs_client.assert_called()
            expected_latest_path = (
                f"metadata/{scenario['metadata_dict']['data']['dockerRepository']}/latest/{scenario['registry_type']}.json"
            )
            mock_bucket.blob.assert_called_with(expected_latest_path)
            mock_blob.exists.assert_called_once()
            mock_bucket.delete_blob.assert_called_once_with(expected_latest_path)
        else:
            # For rc/dev versions, no deletion should occur
            mock_bucket.delete_blob.assert_not_called()

        # Verify NOOP Slack notification
        slack_calls = mock_send_slack.call_args_list
        assert len(slack_calls) == 2  # STARTED + NOOP notifications

        # Check STARTED notification
        start_call = slack_calls[0][0]
        assert "Registry Entry Generation_ STARTED" in start_call[1]
        assert scenario["registry_type"] in start_call[1]

        # Check NOOP notification
        noop_call = slack_calls[1][0]
        assert "Registry Entry Generation_ NOOP" in noop_call[1]
        assert scenario["registry_type"] in noop_call[1]
        assert "not enabled" in noop_call[1]


@pytest.mark.parametrize("registry_type", ["oss", "cloud"])
@patch("metadata_service.registry_entry.send_slack_message")
def test_invalid_metadata_file_path(mock_send_slack, registry_type):
    """Test exception handling when metadata file path doesn't exist or is invalid."""

    # Arrange
    invalid_metadata_path = pathlib.Path("/nonexistent/metadata.yaml")
    spec_path = pathlib.Path("/some/spec.json")  # This won't be reached
    bucket_name = "test-bucket"

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        generate_and_persist_registry_entry(
            bucket_name=bucket_name,
            repo_metadata_file_path=invalid_metadata_path,
            registry_type=registry_type,
            docker_image_tag="irrelevant",
            is_prerelease=False,
        )


@pytest.mark.parametrize(
    "failure_stage,registry_type",
    [
        ("gcs_client", "oss"),
        ("gcs_client", "cloud"),
        ("dependencies_read", "oss"),
        ("dependencies_read", "cloud"),
        ("icon_blob", "oss"),
        ("icon_blob", "cloud"),
        ("persist", "oss"),
        ("persist", "cloud"),
    ],
)
@patch("metadata_service.registry_entry.send_slack_message")
@patch("metadata_service.registry_entry._persist_connector_registry_entry")
@patch("metadata_service.registry_entry._get_icon_blob_from_gcs")
@patch("metadata_service.registry_entry.safe_read_gcs_file")
@patch("metadata_service.registry_entry.get_gcs_storage_client")
def test_gcs_operations_failure(
    mock_gcs_client,
    mock_safe_read_gcs_file,
    mock_get_icon_blob,
    mock_persist_entry,
    mock_send_slack,
    temp_files,
    sample_dependencies_dict,
    failure_stage,
    registry_type,
):
    """Test exception handling when various GCS operations fail."""
    # Arrange
    metadata_path, spec_path = temp_files
    bucket_name = "test-bucket"

    # Mock the failure based on stage
    if failure_stage == "gcs_client":
        mock_gcs_client.side_effect = Exception("GCS client connection failed")
    elif failure_stage == "dependencies_read":
        mock_gcs_client.return_value = Mock()
        mock_safe_read_gcs_file.side_effect = Exception("Failed to read dependencies")
    elif failure_stage == "icon_blob":
        mock_gcs_client.return_value = Mock()
        mock_safe_read_gcs_file.return_value = json.dumps(sample_dependencies_dict)
        mock_get_icon_blob.side_effect = Exception("Failed to get icon blob")
    elif failure_stage == "persist":
        # Mock successful setup until persistence
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_icon_blob = Mock()

        mock_gcs_client.return_value = mock_storage_client
        mock_storage_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = Mock()

        mock_safe_read_gcs_file.return_value = json.dumps(sample_dependencies_dict)
        mock_icon_blob.bucket.name = bucket_name
        mock_icon_blob.name = "metadata/airbyte/source-test/latest/icon.svg"
        mock_get_icon_blob.return_value = mock_icon_blob

        # Fail at persistence
        mock_persist_entry.side_effect = Exception("Failed to persist registry entry")

    # Act & Assert
    with pytest.raises(Exception):
        generate_and_persist_registry_entry(
            bucket_name=bucket_name,
            repo_metadata_file_path=metadata_path,
            registry_type=registry_type,
            docker_image_tag="irrelevant",
            is_prerelease=False,
        )

    # Verify error Slack notification was sent for non-client failures
    if failure_stage != "gcs_client":
        slack_calls = mock_send_slack.call_args_list
        error_calls = [call for call in slack_calls if "FAILED" in call[0][1]]
        assert len(error_calls) >= 1


@pytest.mark.parametrize("registry_type", ["oss", "cloud"])
@patch("metadata_service.registry_entry.send_slack_message")
@patch("metadata_service.registry_entry._apply_metadata_overrides")
def test_metadata_override_application_failure(mock_apply_overrides, mock_send_slack, temp_files, registry_type):
    """Test exception handling when _apply_metadata_overrides fails."""

    # Arrange
    metadata_path, spec_path = temp_files
    bucket_name = "test-bucket"

    # Mock failure during metadata override application
    mock_apply_overrides.side_effect = Exception("Failed to apply metadata overrides")

    # Act & Assert
    with pytest.raises(Exception):
        generate_and_persist_registry_entry(
            bucket_name=bucket_name,
            repo_metadata_file_path=metadata_path,
            registry_type=registry_type,
            docker_image_tag="irrelevant",
            is_prerelease=False,
        )

    # Verify error Slack notification was sent
    slack_calls = mock_send_slack.call_args_list
    error_calls = [call for call in slack_calls if "FAILED" in call[0][1]]
    assert len(error_calls) >= 1


@pytest.mark.parametrize("registry_type", ["oss", "cloud"])
@patch("metadata_service.registry_entry.send_slack_message")
@patch("metadata_service.registry_entry._persist_connector_registry_entry")
@patch("metadata_service.registry_entry._get_icon_blob_from_gcs")
@patch("metadata_service.registry_entry.safe_read_gcs_file")
@patch("metadata_service.registry_entry.get_gcs_storage_client")
@patch("metadata_service.registry_entry._get_connector_type_from_registry_entry")
def test_registry_entry_model_parsing_failure(
    mock_get_connector_type,
    mock_gcs_client,
    mock_safe_read_gcs_file,
    mock_get_icon_blob,
    mock_persist_entry,
    mock_send_slack,
    temp_files,
    sample_dependencies_dict,
    registry_type,
):
    """Test exception handling when pydantic model parsing fails due to invalid data."""

    # Arrange
    metadata_path, spec_path = temp_files
    bucket_name = "test-bucket"

    # Mock successful operations until model parsing
    mock_storage_client = Mock()
    mock_bucket = Mock()
    mock_icon_blob = Mock()

    mock_gcs_client.return_value = mock_storage_client
    mock_storage_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = Mock()

    mock_safe_read_gcs_file.return_value = json.dumps(sample_dependencies_dict)
    mock_icon_blob.bucket.name = bucket_name
    mock_icon_blob.name = "metadata/airbyte/source-test/latest/icon.svg"
    mock_get_icon_blob.return_value = mock_icon_blob

    # Mock model parsing failure
    from metadata_service.models.generated import ConnectorRegistrySourceDefinition

    mock_get_connector_type.return_value = (Mock(), ConnectorRegistrySourceDefinition)

    # Create a mock that fails when parse_obj is called
    mock_model_class = Mock()
    mock_model_class.parse_obj.side_effect = Exception("Invalid model data")
    mock_get_connector_type.return_value = (Mock(), mock_model_class)

    # Act & Assert
    with pytest.raises(Exception):
        generate_and_persist_registry_entry(
            bucket_name=bucket_name,
            repo_metadata_file_path=metadata_path,
            registry_type=registry_type,
            docker_image_tag="irrelevant",
            is_prerelease=False,
        )


# Re-create the temp_files_disabled fixture since it was removed in refactoring
@pytest.fixture
def temp_files_disabled(sample_spec_dict):
    """Create temporary metadata and spec files for disabled registry testing."""
    metadata_dict_disabled = {
        "metadataSpecVersion": "1.0",
        "data": {
            "name": "Test Source Disabled",
            "definitionId": "12345678-1234-1234-1234-123456789012",
            "connectorType": "source",
            "dockerRepository": "airbyte/source-test-disabled",
            "dockerImageTag": "1.0.0",
            "documentationUrl": "https://docs.airbyte.com/integrations/sources/test-disabled",
            "connectorSubtype": "api",
            "releaseStage": "beta",
            "license": "MIT",
            "registryOverrides": {"oss": {"enabled": False}, "cloud": {"enabled": False}},
            "tags": ["language:python"],
        },
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create metadata file
        metadata_path = pathlib.Path(temp_dir) / "metadata.yaml"
        with open(metadata_path, "w") as f:
            yaml.dump(metadata_dict_disabled, f)

        # Create spec file
        spec_path = pathlib.Path(temp_dir) / "spec.json"
        with open(spec_path, "w") as f:
            json.dump(sample_spec_dict, f)

        yield metadata_path, spec_path


# Re-create the temp_files fixture since it was removed in refactoring
@pytest.fixture
def temp_files(sample_spec_dict):
    """Create temporary metadata and spec files for testing."""
    metadata_dict = {
        "metadataSpecVersion": "1.0",
        "data": {
            "name": "Test Source",
            "definitionId": "12345678-1234-1234-1234-123456789012",
            "connectorType": "source",
            "dockerRepository": "airbyte/source-test",
            "dockerImageTag": "1.0.0",
            "documentationUrl": "https://docs.airbyte.com/integrations/sources/test",
            "connectorSubtype": "api",
            "releaseStage": "beta",
            "license": "MIT",
            "registryOverrides": {"oss": {"enabled": True}, "cloud": {"enabled": True}},
            "tags": ["language:python"],
        },
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create metadata file
        metadata_path = pathlib.Path(temp_dir) / "metadata.yaml"
        with open(metadata_path, "w") as f:
            yaml.dump(metadata_dict, f)

        # Create spec file
        spec_path = pathlib.Path(temp_dir) / "spec.json"
        with open(spec_path, "w") as f:
            json.dump(sample_spec_dict, f)

        yield metadata_path, spec_path
