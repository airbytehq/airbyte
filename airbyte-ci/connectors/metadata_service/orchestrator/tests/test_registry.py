from metadata_service.models.generated.ConnectorRegistryV0 import ConnectorRegistryV0


from orchestrator.assets.registry_report import (
    all_sources_dataframe,
    all_destinations_dataframe,
    oss_destinations_dataframe,
    cloud_destinations_dataframe,
    oss_sources_dataframe,
    cloud_sources_dataframe,
)


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

import pytest
from unittest.mock import Mock
from orchestrator.assets.registry import metadata_to_registry_entry, apply_overrides_from_registry

@pytest.mark.parametrize("registry_type, connector_type, expected_id_field",
                         [("cloud", "source", "sourceDefinitionId"),
                          ("cloud", "destination", "destinationDefinitionId"),
                          ("oss", "source", "sourceDefinitionId"),
                          ("oss", "destination", "destinationDefinitionId")])
def test_definition_id_conversion(registry_type, connector_type, expected_id_field):
    """
    Test if the definitionId in the metadata is successfully converted to
    destinationDefinitionId or sourceDefinitionId in the registry entry.
    """
    metadata = {
        "data": {
            "connectorType": connector_type,
            "definitionId": "test-id",
            "registries": {
                registry_type: {
                    "enabled": True
                }
            }
        }
    }

    mock_metadata_entry = Mock()
    mock_metadata_entry.metadata_definition.dict.return_value = metadata
    mock_metadata_entry.icon_url = "test-icon-url"

    result = metadata_to_registry_entry(mock_metadata_entry, connector_type, registry_type)
    assert "definitionId" not in result
    assert result[expected_id_field] == "test-id"
