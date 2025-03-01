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


def test_validation_fail_on_docker_image_tag_decrement(metadata_definition, decremented_version):
    current_version = metadata_definition.data.dockerImageTag

    metadata_definition.data.dockerImageTag = decremented_version
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(metadata_definition, None)
    assert not success
    expected_prefix = f"The dockerImageTag value ({decremented_version}) can't be decremented: it should be equal to or above"
    assert error_message.startswith(expected_prefix), error_message


def test_validation_pass_on_docker_image_tag_increment(metadata_definition, incremented_version):
    metadata_definition.data.dockerImageTag = incremented_version
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(metadata_definition, None)
    assert success
    assert error_message is None


def test_validation_pass_on_same_docker_image_tag(mocker, metadata_definition):
    mocker.patch.object(metadata_validator, "get_latest_version_on_dockerhub", return_value=metadata_definition.data.dockerImageTag)
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(metadata_definition, None)
    assert success
    assert error_message is None


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
