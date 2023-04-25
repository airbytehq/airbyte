from pydash.collections import find

from orchestrator.assets.registry import (
    oss_destinations_dataframe,
    cloud_destinations_dataframe,
    oss_sources_dataframe,
    cloud_sources_dataframe,
)

from orchestrator.assets.metadata import legacy_registry_derived_metadata_definitions

from metadata_service.models.generated.ConnectorRegistryV0 import ConnectorRegistryV0


def test_no_missing_ids(oss_registry_dict, cloud_registry_dict):
    oss_registry_model = ConnectorRegistryV0.parse_obj(oss_registry_dict)
    cloud_registry_model = ConnectorRegistryV0.parse_obj(cloud_registry_dict)

    cloud_destinations_df = cloud_destinations_dataframe(cloud_registry_model).value
    cloud_sources_df = cloud_sources_dataframe(cloud_registry_model).value
    oss_destinations_df = oss_destinations_dataframe(oss_registry_model).value
    oss_sources_df = oss_sources_dataframe(oss_registry_model).value

    metadata_def = legacy_registry_derived_metadata_definitions(
        cloud_sources_df, cloud_destinations_df, oss_sources_df, oss_destinations_df
    ).value
    metadata_definition_ids = [definition["data"]["definitionId"] for definition in metadata_def]
    unique_metadata_definition_ids = set(metadata_definition_ids)

    # assert that all_sources_df has a entry for each sourceDefinitionId in the cloud registry and oss registry
    oss_source_definition_ids = [source["sourceDefinitionId"] for source in oss_registry_dict["sources"]]
    cloud_source_definition_ids = [source["sourceDefinitionId"] for source in cloud_registry_dict["sources"]]
    oss_destination_definition_ids = [destination["destinationDefinitionId"] for destination in oss_registry_dict["destinations"]]
    cloud_destination_definition_ids = [destination["destinationDefinitionId"] for destination in cloud_registry_dict["destinations"]]

    # get all unique ids from the above sets
    all_definition_ids = set(
        oss_source_definition_ids + cloud_source_definition_ids + oss_destination_definition_ids + cloud_destination_definition_ids
    )

    assert unique_metadata_definition_ids == all_definition_ids
    assert len(metadata_definition_ids) == len(unique_metadata_definition_ids)


def assert_in_expected_registry(metadata_def, oss_registry_dict, cloud_registry_dict):
    connectorId = metadata_def["data"]["definitionId"]
    connectorType = metadata_def["data"]["connectorType"]
    enabled_oss = metadata_def["data"]["registries"]["oss"]["enabled"]
    enabled_cloud = metadata_def["data"]["registries"]["cloud"]["enabled"]
    if connectorType == "source":
        is_in_oss = connectorId in [source["sourceDefinitionId"] for source in oss_registry_dict["sources"]]
        is_in_cloud = connectorId in [source["sourceDefinitionId"] for source in cloud_registry_dict["sources"]]
        assert enabled_oss == is_in_oss
        assert enabled_cloud == is_in_cloud
    elif connectorType == "destination":
        is_in_oss = connectorId in [destination["destinationDefinitionId"] for destination in oss_registry_dict["destinations"]]
        is_in_cloud = connectorId in [destination["destinationDefinitionId"] for destination in cloud_registry_dict["destinations"]]
        assert enabled_oss == is_in_oss
        assert enabled_cloud == is_in_cloud
    else:
        raise Exception("Connector type must be either source or destination")


def test_in_correct_registry(oss_registry_dict, cloud_registry_dict):
    oss_registry_model = ConnectorRegistryV0.parse_obj(oss_registry_dict)
    cloud_registry_model = ConnectorRegistryV0.parse_obj(cloud_registry_dict)

    cloud_destinations_df = cloud_destinations_dataframe(cloud_registry_model).value
    cloud_sources_df = cloud_sources_dataframe(cloud_registry_model).value
    oss_destinations_df = oss_destinations_dataframe(oss_registry_model).value
    oss_sources_df = oss_sources_dataframe(oss_registry_model).value

    metadata_def = legacy_registry_derived_metadata_definitions(
        cloud_sources_df, cloud_destinations_df, oss_sources_df, oss_destinations_df
    ).value
    for definition in metadata_def:
        assert_in_expected_registry(definition, oss_registry_dict, cloud_registry_dict)


def has_correct_cloud_docker_image(metadata_def, cloud_registry_dict):
    connectorId = metadata_def["data"]["definitionId"]
    connectorType = metadata_def["data"]["connectorType"]
    enabled_cloud = metadata_def["data"]["registries"]["cloud"]["enabled"]
    if not enabled_cloud:
        return True

    oss_base_docker_image = metadata_def["data"]["dockerRepository"]
    cloud_docker_repo_override = metadata_def["data"]["registries"]["cloud"].get("dockerRepository")
    expected_cloud_docker_repo = cloud_docker_repo_override if cloud_docker_repo_override else oss_base_docker_image

    if connectorType == "source":
        # find the source in the cloud registry
        registry_representation = find(cloud_registry_dict["sources"], {"sourceDefinitionId": connectorId})
        registry_representation = [source for source in cloud_registry_dict["sources"] if source["sourceDefinitionId"] == connectorId][0]
        cloud_docker_image = registry_representation["dockerRepository"]
        return cloud_docker_image == expected_cloud_docker_repo
    elif connectorType == "destination":
        # find the destination in the cloud registry
        registry_representation = find(cloud_registry_dict["destinations"], {"destinationDefinitionId": connectorId})
        cloud_docker_image = registry_representation["dockerRepository"]
        return cloud_docker_image == expected_cloud_docker_repo
    else:
        raise Exception("Connector type must be either source or destination")


def test_registry_override(oss_registry_dict, cloud_registry_dict):
    oss_registry_model = ConnectorRegistryV0.parse_obj(oss_registry_dict)
    cloud_registry_model = ConnectorRegistryV0.parse_obj(cloud_registry_dict)

    cloud_destinations_df = cloud_destinations_dataframe(cloud_registry_model).value
    cloud_sources_df = cloud_sources_dataframe(cloud_registry_model).value
    oss_destinations_df = oss_destinations_dataframe(oss_registry_model).value
    oss_sources_df = oss_sources_dataframe(oss_registry_model).value

    metadata_def = legacy_registry_derived_metadata_definitions(
        cloud_sources_df, cloud_destinations_df, oss_sources_df, oss_destinations_df
    ).value
    for definition in metadata_def:
        assert has_correct_cloud_docker_image(definition, cloud_registry_dict)
