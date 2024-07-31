# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import pytest
import requests
import semver
import yaml
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.validators import metadata_validator


@pytest.fixture
def source_faker_metadata_definition():
    metadata_file_url = (
        "https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-integrations/connectors/source-faker/metadata.yaml"
    )
    response = requests.get(metadata_file_url)
    response.raise_for_status()

    metadata_yaml_dict = yaml.safe_load(response.text)
    return ConnectorMetadataDefinitionV0.parse_obj(metadata_yaml_dict)


@pytest.fixture
def current_version(source_faker_metadata_definition):
    return source_faker_metadata_definition.data.dockerImageTag


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


def test_validation_fail_on_docker_image_tag_decrement(source_faker_metadata_definition, decremented_version):
    current_version = source_faker_metadata_definition.data.dockerImageTag

    source_faker_metadata_definition.data.dockerImageTag = decremented_version
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(source_faker_metadata_definition, None)
    assert not success
    assert error_message == f"The dockerImageTag value can't be decremented: it should be equal to or above {current_version}."


def test_validation_pass_on_docker_image_tag_increment(source_faker_metadata_definition, incremented_version):
    source_faker_metadata_definition.data.dockerImageTag = incremented_version
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(source_faker_metadata_definition, None)
    assert success
    assert error_message is None


def test_validation_pass_on_same_docker_image_tag(source_faker_metadata_definition):
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(source_faker_metadata_definition, None)
    assert success
    assert error_message is None


def test_validation_pass_on_docker_image_no_latest(capsys, source_faker_metadata_definition):
    source_faker_metadata_definition.data.dockerRepository = "airbyte/unreleased"
    success, error_message = metadata_validator.validate_docker_image_tag_is_not_decremented(source_faker_metadata_definition, None)
    captured = capsys.readouterr()
    assert (
        "https://registry.hub.docker.com/v2/repositories/airbyte/unreleased/tags returned a 404. The connector might not be released yet."
        in captured.out
    )
    assert success
    assert error_message is None
