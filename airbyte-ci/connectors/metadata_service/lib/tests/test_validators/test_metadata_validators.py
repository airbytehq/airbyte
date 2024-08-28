# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import pytest
import requests
import semver
import yaml
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.validators import metadata_validator


@pytest.fixture
def metadata_definition():
    metadata_file_url = (
        "https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-integrations/connectors/source-faker/metadata.yaml"
    )
    response = requests.get(metadata_file_url)
    response.raise_for_status()

    metadata_yaml_dict = yaml.safe_load(response.text)
    return ConnectorMetadataDefinitionV0.parse_obj(metadata_yaml_dict)


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
    assert (
        error_message
        == f"The dockerImageTag value ({decremented_version}) can't be decremented: it should be equal to or above {current_version}."
    )


def test_validation_pass_on_docker_image_tag_increment(metadata_definition, incremented_version):
    metadata_definition.data.dockerImageTag = incremented_version
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(metadata_definition, None)
    assert success
    assert error_message is None


def test_validation_pass_on_same_docker_image_tag(metadata_definition):
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
