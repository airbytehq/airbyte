from pydash.collections import find

from orchestrator.assets.catalog import (
    oss_destinations_dataframe,
    cloud_destinations_dataframe,
    oss_sources_dataframe,
    cloud_sources_dataframe,
)

from orchestrator.assets.metadata import catalog_derived_metadata_definitions


def test_no_missing_ids(oss_catalog_dict, cloud_catalog_dict):
    cloud_destinations_df = cloud_destinations_dataframe(cloud_catalog_dict).value
    cloud_sources_df = cloud_sources_dataframe(cloud_catalog_dict).value
    oss_destinations_df = oss_destinations_dataframe(oss_catalog_dict).value
    oss_sources_df = oss_sources_dataframe(oss_catalog_dict).value

    metadata_def = catalog_derived_metadata_definitions(cloud_sources_df, cloud_destinations_df, oss_sources_df, oss_destinations_df).value
    metadata_definition_ids = [definition["data"]["definitionId"] for definition in metadata_def]
    unique_metadata_definition_ids = set(metadata_definition_ids)

    # assert that all_sources_df has a entry for each sourceDefinitionId in the cloud catalog and oss catalog
    oss_source_definition_ids = [source["sourceDefinitionId"] for source in oss_catalog_dict["sources"]]
    cloud_source_definition_ids = [source["sourceDefinitionId"] for source in cloud_catalog_dict["sources"]]
    oss_destination_definition_ids = [destination["destinationDefinitionId"] for destination in oss_catalog_dict["destinations"]]
    cloud_destination_definition_ids = [destination["destinationDefinitionId"] for destination in cloud_catalog_dict["destinations"]]

    # get all unique ids from the above sets
    all_definition_ids = set(
        oss_source_definition_ids + cloud_source_definition_ids + oss_destination_definition_ids + cloud_destination_definition_ids
    )

    assert unique_metadata_definition_ids == all_definition_ids
    assert len(metadata_definition_ids) == len(unique_metadata_definition_ids)


def assert_in_expected_catalog(metadata_def, oss_catalog_dict, cloud_catalog_dict):
    connectorId = metadata_def["data"]["definitionId"]
    connectorType = metadata_def["data"]["connectorType"]
    enabled_oss = metadata_def["data"]["catalogs"]["oss"]["enabled"]
    enabled_cloud = metadata_def["data"]["catalogs"]["cloud"]["enabled"]
    if connectorType == "source":
        is_in_oss = connectorId in [source["sourceDefinitionId"] for source in oss_catalog_dict["sources"]]
        is_in_cloud = connectorId in [source["sourceDefinitionId"] for source in cloud_catalog_dict["sources"]]
        assert enabled_oss == is_in_oss
        assert enabled_cloud == is_in_cloud
    elif connectorType == "destination":
        is_in_oss = connectorId in [destination["destinationDefinitionId"] for destination in oss_catalog_dict["destinations"]]
        is_in_cloud = connectorId in [destination["destinationDefinitionId"] for destination in cloud_catalog_dict["destinations"]]
        assert enabled_oss == is_in_oss
        assert enabled_cloud == is_in_cloud
    else:
        raise Exception("Connector type must be either source or destination")


def test_in_correct_catalog(oss_catalog_dict, cloud_catalog_dict):
    cloud_destinations_df = cloud_destinations_dataframe(cloud_catalog_dict).value
    cloud_sources_df = cloud_sources_dataframe(cloud_catalog_dict).value
    oss_destinations_df = oss_destinations_dataframe(oss_catalog_dict).value
    oss_sources_df = oss_sources_dataframe(oss_catalog_dict).value

    metadata_def = catalog_derived_metadata_definitions(cloud_sources_df, cloud_destinations_df, oss_sources_df, oss_destinations_df).value
    for definition in metadata_def:
        assert_in_expected_catalog(definition, oss_catalog_dict, cloud_catalog_dict)


def has_correct_cloud_docker_image(metadata_def, cloud_catalog_dict):
    connectorId = metadata_def["data"]["definitionId"]
    connectorType = metadata_def["data"]["connectorType"]
    enabled_cloud = metadata_def["data"]["catalogs"]["cloud"]["enabled"]
    if not enabled_cloud:
        return True

    oss_base_docker_image = metadata_def["data"]["dockerRepository"]
    cloud_docker_repo_override = metadata_def["data"]["catalogs"]["cloud"].get("dockerRepository")
    expected_cloud_docker_repo = cloud_docker_repo_override if cloud_docker_repo_override else oss_base_docker_image

    if connectorType == "source":
        # find the source in the cloud catalog
        catalog_representation = find(cloud_catalog_dict["sources"], {"sourceDefinitionId": connectorId})
        catalog_representation = [source for source in cloud_catalog_dict["sources"] if source["sourceDefinitionId"] == connectorId][0]
        cloud_docker_image = catalog_representation["dockerRepository"]
        return cloud_docker_image == expected_cloud_docker_repo
    elif connectorType == "destination":
        # find the destination in the cloud catalog
        catalog_representation = find(cloud_catalog_dict["destinations"], {"destinationDefinitionId": connectorId})
        cloud_docker_image = catalog_representation["dockerRepository"]
        return cloud_docker_image == expected_cloud_docker_repo
    else:
        raise Exception("Connector type must be either source or destination")


def test_catalog_override(oss_catalog_dict, cloud_catalog_dict):
    cloud_destinations_df = cloud_destinations_dataframe(cloud_catalog_dict).value
    cloud_sources_df = cloud_sources_dataframe(cloud_catalog_dict).value
    oss_destinations_df = oss_destinations_dataframe(oss_catalog_dict).value
    oss_sources_df = oss_sources_dataframe(oss_catalog_dict).value

    metadata_def = catalog_derived_metadata_definitions(cloud_sources_df, cloud_destinations_df, oss_sources_df, oss_destinations_df).value
    for definition in metadata_def:
        assert has_correct_cloud_docker_image(definition, cloud_catalog_dict)
