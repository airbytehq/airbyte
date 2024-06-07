#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest import mock
from uuid import UUID

import pytest
import yaml
from google.cloud import storage
from metadata_service.models.generated.ConnectorRegistryDestinationDefinition import ConnectorRegistryDestinationDefinition
from metadata_service.models.generated.ConnectorRegistrySourceDefinition import ConnectorRegistrySourceDefinition
from metadata_service.models.generated.ConnectorRegistryV0 import ConnectorRegistryV0
from orchestrator.assets.registry_entry import (
    get_connector_type_from_registry_entry,
    get_registry_entry_write_path,
    get_registry_status_lists,
    metadata_to_registry_entry,
    safe_parse_metadata_definition,
)
from orchestrator.assets.registry_report import (
    all_destinations_dataframe,
    all_sources_dataframe,
    cloud_destinations_dataframe,
    cloud_sources_dataframe,
    oss_destinations_dataframe,
    oss_sources_dataframe,
)
from orchestrator.models.metadata import LatestMetadataEntry, MetadataDefinition
from orchestrator.utils.blob_helpers import yaml_blob_to_dict
from pydantic import ValidationError

VALID_METADATA_DICT = {
    "metadataSpecVersion": "1.0",
    "data": {
        "name": "Test",
        "definitionId": str(UUID(int=1)),
        "connectorType": "source",
        "dockerRepository": "test_repo",
        "dockerImageTag": "test_tag",
        "license": "test_license",
        "documentationUrl": "https://test_documentation_url.com",
        "githubIssueLabel": "test_label",
        "connectorSubtype": "api",
        "supportLevel": "community",
        "releaseStage": "alpha",
        "registries": {"oss": {"enabled": True}, "cloud": {"enabled": True}},
    },
}
INVALID_METADATA_DICT = {"invalid": "metadata"}


@pytest.mark.parametrize(
    "blob_name, blob_content, expected_result, expected_exception",
    [
        ("1.2.3/metadata.yaml", yaml.dump(VALID_METADATA_DICT), MetadataDefinition.parse_obj(VALID_METADATA_DICT), None),
        ("latest/metadata.yaml", yaml.dump(VALID_METADATA_DICT), MetadataDefinition.parse_obj(VALID_METADATA_DICT), None),
        ("1.2.3/metadata.yaml", yaml.dump(INVALID_METADATA_DICT), None, None),
        ("latest/metadata.yaml", yaml.dump(INVALID_METADATA_DICT), None, ValidationError),
    ],
)
def test_safe_parse_metadata_definition(blob_name, blob_content, expected_result, expected_exception):
    # Mock the Blob object
    mock_blob = mock.create_autospec(storage.Blob, instance=True)
    mock_blob.name = blob_name
    mock_blob.download_as_string.return_value = blob_content.encode("utf-8")

    metadata_dict = yaml_blob_to_dict(mock_blob)

    if expected_exception:
        with pytest.raises(expected_exception):
            safe_parse_metadata_definition(mock_blob.name, metadata_dict)
    else:
        result = safe_parse_metadata_definition(mock_blob.name, metadata_dict)
        # assert the name is set correctly
        assert result == expected_result


@pytest.mark.parametrize(
    "registries_data, expected_enabled, expected_disabled",
    [
        (
            {"oss": {"enabled": True}, "cloud": {"enabled": True}},
            ["oss", "cloud"],
            [],
        ),
        (
            {"oss": {"enabled": False}, "cloud": {"enabled": True}},
            ["cloud"],
            ["oss"],
        ),
        (
            {"oss": {"enabled": False}, "cloud": {"enabled": False}},
            [],
            ["oss", "cloud"],
        ),
        (
            {"oss": {"enabled": False}, "cloud": None},
            [],
            ["oss", "cloud"],
        ),
        (
            {"oss": {"enabled": False}},
            [],
            ["oss", "cloud"],
        ),
        (
            None,
            [],
            ["oss", "cloud"],
        ),
        (
            {"oss": {"enabled": True}},
            ["oss"],
            ["cloud"],
        ),
    ],
)
def test_get_registry_status_lists(registries_data, expected_enabled, expected_disabled):
    metadata_dict = {
        "metadataSpecVersion": "1.0",
        "data": {
            "name": "Test",
            "definitionId": str(UUID(int=1)),
            "connectorType": "source",
            "dockerRepository": "test_repo",
            "dockerImageTag": "test_tag",
            "license": "test_license",
            "documentationUrl": "https://test_documentation_url.com",
            "githubIssueLabel": "test_label",
            "connectorSubtype": "api",
            "releaseStage": "alpha",
            "supportLevel": "community",
            "registries": registries_data,
        },
    }
    metadata_definition = MetadataDefinition.parse_obj(metadata_dict)
    registry_entry = LatestMetadataEntry(metadata_definition=metadata_definition)
    enabled, disabled = get_registry_status_lists(registry_entry)
    assert set(enabled) == set(expected_enabled)
    assert set(disabled) == set(expected_disabled)


@pytest.mark.parametrize(
    "registry_entry, expected_type, expected_class",
    [
        ({"sourceDefinitionId": "abc"}, "source", ConnectorRegistrySourceDefinition),
        ({"destinationDefinitionId": "abc"}, "destination", ConnectorRegistryDestinationDefinition),
        ({}, None, None),
    ],
)
def test_get_connector_type_from_registry_entry(registry_entry, expected_type, expected_class):
    if expected_type and expected_class:
        connector_type, connector_class = get_connector_type_from_registry_entry(registry_entry)
        assert connector_type == expected_type
        assert connector_class == expected_class
    else:
        with pytest.raises(Exception) as e_info:
            get_connector_type_from_registry_entry(registry_entry)
        assert str(e_info.value) == "Could not determine connector type from registry entry"


def test_merged_registry_dataframes(oss_registry_dict, cloud_registry_dict):
    oss_registry_model = ConnectorRegistryV0.parse_obj(oss_registry_dict)
    cloud_registry_model = ConnectorRegistryV0.parse_obj(cloud_registry_dict)

    github_connector_folders = []
    num_oss_destinations = len(oss_registry_dict["destinations"])
    num_cloud_destinations = len(cloud_registry_dict["destinations"])

    num_cloud_sources = len(cloud_registry_dict["sources"])
    num_oss_sources = len(oss_registry_dict["sources"])

    cloud_destinations_df = cloud_destinations_dataframe(cloud_registry_model).value
    assert len(cloud_destinations_df) == num_cloud_destinations

    cloud_sources_df = cloud_sources_dataframe(cloud_registry_model).value
    assert len(cloud_sources_df) == num_cloud_sources

    oss_destinations_df = oss_destinations_dataframe(oss_registry_model).value
    assert len(oss_destinations_df) == num_oss_destinations

    oss_sources_df = oss_sources_dataframe(oss_registry_model).value
    assert len(oss_sources_df) == num_oss_sources

    all_sources_df = all_sources_dataframe(cloud_sources_df, oss_sources_df, github_connector_folders)
    all_destinations_df = all_destinations_dataframe(cloud_destinations_df, oss_destinations_df, github_connector_folders)

    # assert that all_sources_df has a entry for each sourceDefinitionId in the cloud registry and oss registry
    oss_source_definition_ids = set([source["sourceDefinitionId"] for source in oss_registry_dict["sources"]])
    cloud_source_definition_ids = set([source["sourceDefinitionId"] for source in cloud_registry_dict["sources"]])
    all_source_definition_ids = set(all_sources_df["definitionId"])

    assert all_source_definition_ids == oss_source_definition_ids.union(cloud_source_definition_ids)

    # assert that all_destinations_df has a entry for each sourceDefinitionId in the cloud registry and oss registry
    oss_destination_definition_ids = set([destination["destinationDefinitionId"] for destination in oss_registry_dict["destinations"]])
    cloud_destination_definition_ids = set([destination["destinationDefinitionId"] for destination in cloud_registry_dict["destinations"]])
    all_destination_definition_ids = set(all_destinations_df["definitionId"])

    assert all_destination_definition_ids == oss_destination_definition_ids.union(cloud_destination_definition_ids)


@pytest.mark.parametrize(
    "registry_type, connector_type, expected_id_field",
    [
        ("cloud", "source", "sourceDefinitionId"),
        ("cloud", "destination", "destinationDefinitionId"),
        ("oss", "source", "sourceDefinitionId"),
        ("oss", "destination", "destinationDefinitionId"),
    ],
)
def test_definition_id_conversion(registry_type, connector_type, expected_id_field):
    """
    Test if the definitionId in the metadata is successfully converted to
    destinationDefinitionId or sourceDefinitionId in the registry entry.
    """
    metadata = {"data": {"connectorType": connector_type, "definitionId": "test-id", "registries": {registry_type: {"enabled": True}}}}

    mock_metadata_entry = mock.Mock()
    mock_metadata_entry.metadata_definition.dict.return_value = metadata
    mock_metadata_entry.icon_url = "test-icon-url"

    result = metadata_to_registry_entry(mock_metadata_entry, registry_type)
    assert "definitionId" not in result
    assert "test-id" == result[expected_id_field]


def test_tombstone_custom_public_set():
    """
    Test if tombstone, custom and public are set correctly in the registry entry.
    """
    metadata = {"data": {"connectorType": "source", "definitionId": "test-id", "registries": {"oss": {"enabled": True}}}}

    mock_metadata_entry = mock.Mock()
    mock_metadata_entry.metadata_definition.dict.return_value = metadata
    mock_metadata_entry.icon_url = "test-icon-url"

    result = metadata_to_registry_entry(mock_metadata_entry, "oss")
    assert result["tombstone"] is False
    assert result["custom"] is False
    assert result["public"] is True


def test_fields_deletion():
    """
    Test if registries, connectorType, and definitionId fields were deleted from the registry entry.
    """
    metadata = {"data": {"connectorType": "source", "definitionId": "test-id", "registries": {"oss": {"enabled": True}}}}

    mock_metadata_entry = mock.Mock()
    mock_metadata_entry.metadata_definition.dict.return_value = metadata
    mock_metadata_entry.icon_url = "test-icon-url"

    result = metadata_to_registry_entry(mock_metadata_entry, "oss")
    assert "registries" not in result
    assert "connectorType" not in result
    assert "definitionId" not in result


@pytest.mark.parametrize(
    "registry_type, expected_docker_image_tag, expected_additional_field",
    [("cloud", "cloud_tag", "cloud_value"), ("oss", "oss_tag", "oss_value")],
)
def test_overrides_application(registry_type, expected_docker_image_tag, expected_additional_field):
    """
    Test if the overrides for cloud or oss are properly applied to the registry entry.
    """
    # Assuming 'overriddenField' is a field to be overridden in metadata for the sake of this test.
    metadata = {
        "data": {
            "connectorType": "source",
            "definitionId": "test-id",
            "dockerImageTag": "base_tag",
            "registries": {
                "oss": {"enabled": True, "dockerImageTag": "oss_tag", "additionalField": "oss_value"},
                "cloud": {"enabled": True, "dockerImageTag": "cloud_tag", "additionalField": "cloud_value"},
            },
        }
    }

    mock_metadata_entry = mock.Mock()
    mock_metadata_entry.metadata_definition.dict.return_value = metadata
    mock_metadata_entry.file_path = f"metadata/{expected_docker_image_tag}/metadata.yaml"
    mock_metadata_entry.icon_url = "test-icon-url"

    registry_entry = metadata_to_registry_entry(mock_metadata_entry, registry_type)
    assert registry_entry["dockerImageTag"] == expected_docker_image_tag
    assert registry_entry["additionalField"] == expected_additional_field

    expected_write_path = f"metadata/{expected_docker_image_tag}/{registry_type}"
    assert get_registry_entry_write_path(registry_entry, mock_metadata_entry, registry_type) == expected_write_path


def test_source_type_extraction():
    """
    Test if sourceType is successfully extracted from connectorSubtype in the registry entry.
    """
    metadata = {
        "data": {
            "connectorType": "source",
            "connectorSubtype": "database",
            "definitionId": "test-id",
            "registries": {"oss": {"enabled": True}},
        }
    }

    mock_metadata_entry = mock.Mock()
    mock_metadata_entry.metadata_definition.dict.return_value = metadata
    mock_metadata_entry.icon_url = "test-icon-url"

    result = metadata_to_registry_entry(mock_metadata_entry, "oss")
    assert result["sourceType"] == "database"


def test_support_level_default():
    """
    Test if supportLevel is defaulted to alpha in the registry entry.
    """
    metadata = {"data": {"connectorType": "source", "definitionId": "test-id", "registries": {"oss": {"enabled": True}}}}

    mock_metadata_entry = mock.Mock()
    mock_metadata_entry.metadata_definition.dict.return_value = metadata
    mock_metadata_entry.icon_url = "test-icon-url"

    result = metadata_to_registry_entry(mock_metadata_entry, "oss")
    assert result["supportLevel"] == "community"


def test_migration_documentation_url_default():
    """
    Test if migrationDocumentationUrl is successfully defaulted in releases.migrationDocumentationUrl in the registry entry.
    """
    metadata = {
        "data": {
            "connectorType": "source",
            "definitionId": "test-id",
            "documentationUrl": "test-doc-url",
            "registries": {"oss": {"enabled": True}},
            "releases": {"migrationDocumentationUrl": None, "breakingChanges": {"1.0.0": {"migrationDocumentationUrl": None}}},
        }
    }

    mock_metadata_entry = mock.Mock()
    mock_metadata_entry.metadata_definition.dict.return_value = metadata
    mock_metadata_entry.icon_url = "test-icon-url"

    expected_top_migration_documentation_url = "test-doc-url-migrations"
    expected_version_migration_documentation_url = "test-doc-url-migrations#1.0.0"

    result = metadata_to_registry_entry(mock_metadata_entry, "oss")
    assert result["releases"]["migrationDocumentationUrl"] == expected_top_migration_documentation_url
    assert result["releases"]["breakingChanges"]["1.0.0"]["migrationDocumentationUrl"] == expected_version_migration_documentation_url


def test_breaking_changes_migration_documentation_url():
    """
    Test if migrationDocumentationUrl is successfully defaulted for all entries in releases.breakingChanges including the key as the version.
    """
    metadata = {
        "data": {
            "connectorType": "source",
            "definitionId": "test-id",
            "documentationUrl": "test-doc-url",
            "registries": {"oss": {"enabled": True}},
            "releases": {
                "migrationDocumentationUrl": "test-migration-doc-url",
                "breakingChanges": {"1.0.0": {"migrationDocumentationUrl": "test-migration-doc-url-version"}},
            },
        }
    }

    mock_metadata_entry = mock.Mock()
    mock_metadata_entry.metadata_definition.dict.return_value = metadata
    mock_metadata_entry.icon_url = "test-icon-url"

    result = metadata_to_registry_entry(mock_metadata_entry, "oss")
    assert result["releases"]["migrationDocumentationUrl"] == "test-migration-doc-url"
    assert result["releases"]["breakingChanges"]["1.0.0"]["migrationDocumentationUrl"] == "test-migration-doc-url-version"


def test_icon_url():
    """
    Test if the iconUrl in the metadata entry is correctly set in the registry entry.
    """
    metadata = {"data": {"connectorType": "source", "definitionId": "test-id", "registries": {"oss": {"enabled": True}}}}

    mock_metadata_entry = mock.Mock()
    mock_metadata_entry.metadata_definition.dict.return_value = metadata
    mock_metadata_entry.icon_url = "test-icon-url"

    result = metadata_to_registry_entry(mock_metadata_entry, "oss")
    assert result["iconUrl"] == "test-icon-url"
