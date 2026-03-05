# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
import requests
import semver
import yaml

from metadata_service.docker_hub import get_latest_version_on_dockerhub
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.validators import metadata_validator


@pytest.fixture
def metadata_definition():
    return ConnectorMetadataDefinitionV0.parse_obj(
        {
            "data": {
                "ab_internal": {"ql": 300, "sl": 100},
                "allowedHosts": {"hosts": []},
                "connectorBuildOptions": {
                    "baseImage": "docker.io/airbyte/python-connector-base:2.0.0@sha256:c44839ba84406116e8ba68722a0f30e8f6e7056c726f447681bb9e9ece8bd916"
                },
                "connectorSubtype": "api",
                "connectorType": "source",
                "definitionId": "dfd88b22-b603-4c3d-aad7-3701784586b1",
                "dockerImageTag": "6.2.18-rc.1",
                "dockerRepository": "airbyte/source-faker",
                "documentationUrl": "https://docs.airbyte.com/integrations/sources/faker",
                "githubIssueLabel": "source-faker",
                "icon": "faker.svg",
                "license": "MIT",
                "name": "Sample Data (Faker)",
                "registryOverrides": {"cloud": {"enabled": True}, "oss": {"enabled": True}},
                "releaseStage": "beta",
                "releases": {
                    "rolloutConfiguration": {"enableProgressiveRollout": True},
                    "breakingChanges": {
                        "4.0.0": {"message": "This is a breaking change message", "upgradeDeadline": "2023-07-19"},
                        "5.0.0": {
                            "message": "ID and products.year fields are changing to be integers instead of floats.",
                            "upgradeDeadline": "2023-08-31",
                        },
                        "6.0.0": {"message": "Declare 'id' columns as primary keys.", "upgradeDeadline": "2024-04-01"},
                    },
                },
                "remoteRegistries": {"pypi": {"enabled": True, "packageName": "airbyte-source-faker"}},
                "resourceRequirements": {
                    "jobSpecific": [{"jobType": "sync", "resourceRequirements": {"cpu_limit": "4.0", "cpu_request": "1.0"}}]
                },
                "suggestedStreams": {"streams": ["users", "products", "purchases"]},
                "supportLevel": "community",
                "tags": ["language:python", "cdk:python"],
                "connectorTestSuitesOptions": [
                    {
                        "suite": "liveTests",
                        "testConnections": [{"name": "faker_config_dev_null", "id": "73abc3a9-3fea-4e7c-b58d-2c8236464a95"}],
                    },
                    {"suite": "unitTests"},
                    {
                        "suite": "acceptanceTests",
                        "testSecrets": [
                            {
                                "name": "SECRET_SOURCE-FAKER_CREDS",
                                "fileName": "config.json",
                                "secretStore": {"type": "GSM", "alias": "airbyte-connector-testing-secret-store"},
                            }
                        ],
                    },
                ],
            },
            "metadataSpecVersion": "1.0",
        }
    )


@pytest.mark.slow
@pytest.mark.parametrize(
    "latest_version, current_version,should_pass_validation",
    [("1.0.0", "0.1.0", False), ("1.0.0", "1.0.0", True), ("1.0.0", "1.1.0", True)],
)
def test_validate_docker_image_tag_is_not_decremented(mocker, metadata_definition, latest_version, current_version, should_pass_validation):
    mocker.patch.object(metadata_validator, "get_latest_version_on_dockerhub", return_value=latest_version)
    metadata_definition.data.dockerImageTag = current_version
    passed_validation, _ = metadata_validator.validate_docker_image_tag_is_not_decremented(metadata_definition, None)
    assert passed_validation == should_pass_validation


@pytest.fixture
def current_version(metadata_definition):
    return metadata_definition.data.dockerImageTag


@pytest.fixture
def decremented_version(current_version):
    version_info = semver.VersionInfo.parse(current_version)
    if version_info.major > 0:
        patched_version_info = version_info.replace(major=version_info.major - 1)
    elif version_info.minor > 0:
        patched_version_info = version_info.replace(major=version_info.minor - 1)
    elif version_info.patch > 0:
        patched_version_info = version_info.replace(patch=version_info.patch - 1)
    else:
        raise ValueError(f"Version {version_info} can't be decremented to prepare our test")
    return str(patched_version_info)


@pytest.fixture
def incremented_version(current_version):
    version_info = semver.VersionInfo.parse(current_version)
    if version_info.major > 0:
        patched_version_info = version_info.replace(major=version_info.major + 1)
    elif version_info.minor > 0:
        patched_version_info = version_info.replace(major=version_info.minor + 1)
    elif version_info.patch > 0:
        patched_version_info = version_info.replace(patch=version_info.patch + 1)
    else:
        raise ValueError(f"Version {version_info} can't be incremented to prepare our test")
    return str(patched_version_info)


@pytest.mark.slow
def test_validation_fail_on_docker_image_tag_decrement(metadata_definition, decremented_version):
    current_version = metadata_definition.data.dockerImageTag

    metadata_definition.data.dockerImageTag = decremented_version
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(metadata_definition, None)
    assert not success
    expected_prefix = f"The dockerImageTag value ({decremented_version}) can't be decremented: it should be equal to or above"
    assert error_message.startswith(expected_prefix), error_message


@pytest.mark.slow
def test_validation_pass_on_docker_image_tag_increment(metadata_definition, incremented_version):
    metadata_definition.data.dockerImageTag = incremented_version
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(metadata_definition, None)
    assert success
    assert error_message is None


@pytest.mark.slow
def test_validation_pass_on_same_docker_image_tag(mocker, metadata_definition):
    mocker.patch.object(metadata_validator, "get_latest_version_on_dockerhub", return_value=metadata_definition.data.dockerImageTag)
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(metadata_definition, None)
    assert success
    assert error_message is None


@pytest.mark.slow
def test_validation_pass_on_docker_image_no_latest(capsys, metadata_definition):
    metadata_definition.data.dockerRepository = "airbyte/unreleased"
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(metadata_definition, None)
    captured = capsys.readouterr()
    assert (
        "https://registry.hub.docker.com/v2/repositories/airbyte/unreleased/tags returned a 404. The connector might not be released yet."
        in captured.out
    )
    assert success
    assert error_message is None


# ---- Tests for validate_docs_has_supported_sync_modes_table ----

VALID_SYNC_MODES_DOC = """\
# My Destination

Some intro text.

## Supported sync modes

The destination supports the following sync modes:

| Sync mode | Supported? |
| :--- | :---: |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | Yes |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

## Changelog
"""

MISSING_HEADING_DOC = """\
# My Destination

Some intro text.

| Sync mode | Supported? |
| :--- | :---: |
| Full Refresh - Overwrite | Yes |
| Full Refresh - Append | Yes |
| Full Refresh - Overwrite + Deduped | Yes |
| Incremental Sync - Append | Yes |
| Incremental Sync - Append + Deduped | Yes |
"""

MISSING_TABLE_DOC = """\
# My Destination

## Supported sync modes

This destination supports full refresh and incremental modes.
"""

MISSING_SYNC_MODES_DOC = """\
# My Destination

## Supported sync modes

| Sync mode | Supported? |
| :--- | :---: |
| Full Refresh - Overwrite | Yes |
| Full Refresh - Append | Yes |
| Full Refresh - Overwrite + Deduped | Yes |
"""


@pytest.fixture
def destination_metadata_definition():
    """A metadata definition for an enabled destination connector."""
    return ConnectorMetadataDefinitionV0.parse_obj(
        {
            "data": {
                "ab_internal": {"ql": 300, "sl": 100},
                "connectorSubtype": "database",
                "connectorType": "destination",
                "definitionId": "22f6c74f-5699-40ff-833c-4a879ea40133",
                "dockerImageTag": "1.0.0",
                "dockerRepository": "airbyte/destination-test",
                "documentationUrl": "https://docs.airbyte.com/integrations/destinations/test",
                "githubIssueLabel": "destination-test",
                "icon": "test.svg",
                "license": "MIT",
                "name": "Test Destination",
                "registryOverrides": {"cloud": {"enabled": True}, "oss": {"enabled": True}},
                "releaseStage": "generally_available",
                "supportLevel": "certified",
                "tags": ["language:java"],
            },
            "metadataSpecVersion": "1.0",
        }
    )


@pytest.fixture
def disabled_destination_metadata():
    """A metadata definition for a disabled/archived destination connector."""
    return ConnectorMetadataDefinitionV0.parse_obj(
        {
            "data": {
                "ab_internal": {"ql": 300, "sl": 100},
                "connectorSubtype": "database",
                "connectorType": "destination",
                "definitionId": "22f6c74f-5699-40ff-833c-4a879ea40133",
                "dockerImageTag": "1.0.0",
                "dockerRepository": "airbyte/destination-archived",
                "documentationUrl": "https://docs.airbyte.com/integrations/destinations/archived",
                "githubIssueLabel": "destination-archived",
                "icon": "archived.svg",
                "license": "MIT",
                "name": "Archived Destination",
                "registryOverrides": {"cloud": {"enabled": False}, "oss": {"enabled": False}},
                "releaseStage": "alpha",
                "supportLevel": "archived",
                "tags": ["language:java"],
            },
            "metadataSpecVersion": "1.0",
        }
    )


def test_sync_modes_validator_passes_for_valid_doc(tmp_path, destination_metadata_definition):
    """Validator passes when the doc has a proper 'Supported sync modes' section."""
    doc_file = tmp_path / "test-destination.md"
    doc_file.write_text(VALID_SYNC_MODES_DOC)
    opts = metadata_validator.ValidatorOptions(docs_path=str(doc_file))
    success, error = metadata_validator.validate_docs_has_supported_sync_modes_table(destination_metadata_definition, opts)
    assert success
    assert error is None


def test_sync_modes_validator_skips_source_connectors(tmp_path, metadata_definition):
    """Validator skips source connectors (existing fixture is a source)."""
    doc_file = tmp_path / "source.md"
    doc_file.write_text("# No sync modes table here")
    opts = metadata_validator.ValidatorOptions(docs_path=str(doc_file))
    success, error = metadata_validator.validate_docs_has_supported_sync_modes_table(metadata_definition, opts)
    assert success
    assert error is None


def test_sync_modes_validator_skips_disabled_destinations(tmp_path, disabled_destination_metadata):
    """Validator skips destinations that are disabled in both OSS and Cloud."""
    doc_file = tmp_path / "archived.md"
    doc_file.write_text("# No sync modes table here")
    opts = metadata_validator.ValidatorOptions(docs_path=str(doc_file))
    success, error = metadata_validator.validate_docs_has_supported_sync_modes_table(disabled_destination_metadata, opts)
    assert success
    assert error is None


def test_sync_modes_validator_fails_missing_heading(tmp_path, destination_metadata_definition):
    """Validator fails when the doc has a table but no '## Supported sync modes' heading."""
    doc_file = tmp_path / "test-destination.md"
    doc_file.write_text(MISSING_HEADING_DOC)
    opts = metadata_validator.ValidatorOptions(docs_path=str(doc_file))
    success, error = metadata_validator.validate_docs_has_supported_sync_modes_table(destination_metadata_definition, opts)
    assert not success
    assert "must contain a '## Supported sync modes' section" in error


def test_sync_modes_validator_fails_missing_table(tmp_path, destination_metadata_definition):
    """Validator fails when the doc has the heading but no markdown table."""
    doc_file = tmp_path / "test-destination.md"
    doc_file.write_text(MISSING_TABLE_DOC)
    opts = metadata_validator.ValidatorOptions(docs_path=str(doc_file))
    success, error = metadata_validator.validate_docs_has_supported_sync_modes_table(destination_metadata_definition, opts)
    assert not success
    assert "missing the expected markdown table" in error


def test_sync_modes_validator_fails_missing_sync_modes(tmp_path, destination_metadata_definition):
    """Validator fails when some required sync modes are missing from the table."""
    doc_file = tmp_path / "test-destination.md"
    doc_file.write_text(MISSING_SYNC_MODES_DOC)
    opts = metadata_validator.ValidatorOptions(docs_path=str(doc_file))
    success, error = metadata_validator.validate_docs_has_supported_sync_modes_table(destination_metadata_definition, opts)
    assert not success
    assert "Incremental Sync - Append" in error
    assert "Incremental Sync - Append + Deduped" in error


def test_sync_modes_validator_skips_nonexistent_docs(tmp_path, destination_metadata_definition):
    """Validator skips if the docs file doesn't exist (validate_docs_path_exists handles that)."""
    opts = metadata_validator.ValidatorOptions(docs_path=str(tmp_path / "nonexistent.md"))
    success, error = metadata_validator.validate_docs_has_supported_sync_modes_table(destination_metadata_definition, opts)
    assert success
    assert error is None
