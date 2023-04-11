import pandas as pd
import json
from typing import List

from dagster import asset, OpExecutionContext

from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe
from orchestrator.utils.object_helpers import deep_copy_params
from orchestrator.models.metadata import PartialMetadataDefinition


GROUP_NAME = "catalog"

# HELPERS


@deep_copy_params
def apply_overrides_from_catalog(metadata_data: dict, override_catalog_key: str) -> dict:
    """Apply the overrides from the catalog to the metadata data.

    Args:
        metadata_data (dict): The metadata data field.
        override_catalog_key (str): The key of the catalog to override the metadata with.

    Returns:
        dict: The metadata data field with the overrides applied.
    """
    override_catalog = metadata_data["catalogs"][override_catalog_key]
    del override_catalog["enabled"]
    metadata_data.update(override_catalog)

    return metadata_data


@deep_copy_params
def metadata_to_catalog_entry(metadata_definition: dict, connector_type: str, override_catalog_key: str) -> dict:
    """Convert the metadata definition to a catalog entry.

    Args:
        metadata_definition (dict): The metadata definition.
        connector_type (str): One of "source" or "destination".
        override_catalog_key (str): The key of the catalog to override the metadata with.

    Returns:
        dict: The catalog equivalent of the metadata definition.
    """
    metadata_data = metadata_definition["data"]

    overrode_metadata_data = apply_overrides_from_catalog(metadata_data, override_catalog_key)
    del overrode_metadata_data["catalogs"]

    del overrode_metadata_data["connectorType"]

    # rename field connectorSubtype to sourceType
    connection_type = overrode_metadata_data.get("connectorSubtype")
    if connection_type:
        overrode_metadata_data["sourceType"] = overrode_metadata_data["connectorSubtype"]
        del overrode_metadata_data["connectorSubtype"]

    # rename supportUrl to documentationUrl
    support_url = overrode_metadata_data.get("supportUrl")
    if support_url:
        overrode_metadata_data["documentationUrl"] = overrode_metadata_data["supportUrl"]
        del overrode_metadata_data["supportUrl"]

    # rename definitionId field to sourceDefinitionId or destinationDefinitionId
    id_field = "sourceDefinitionId" if connector_type == "source" else "destinationDefinitionId"
    overrode_metadata_data[id_field] = overrode_metadata_data["definitionId"]
    del overrode_metadata_data["definitionId"]

    # add in useless fields that are currently required for porting to the actor definition spec
    overrode_metadata_data["tombstone"] = False
    overrode_metadata_data["custom"] = False
    overrode_metadata_data["public"] = True

    # if there is no releaseStage, set it to "alpha"
    # Note: this is something our current cloud catalog generator does
    # Note: We will not once this is live
    if not overrode_metadata_data.get("releaseStage"):
        overrode_metadata_data["releaseStage"] = "alpha"

    return overrode_metadata_data


def is_metadata_catalog_enabled(metadata_definition: dict, catalog_name: str) -> bool:
    return metadata_definition["data"]["catalogs"][catalog_name]["enabled"]


def is_metadata_connector_type(metadata_definition: dict, connector_type: str) -> bool:
    return metadata_definition["data"]["connectorType"] == connector_type


def construct_catalog_from_metadata(catalog_derived_metadata_definitions: List[PartialMetadataDefinition], catalog_name: str) -> dict:
    """Construct the catalog from the metadata definitions.

    Args:
        catalog_derived_metadata_definitions (List[dict]): Metadata definitions that have been derived from the existing catalog.
        catalog_name (str): The name of the catalog to construct. One of "cloud" or "oss".

    Returns:
        dict: The catalog.
    """
    catalog_sources = [
        metadata_to_catalog_entry(metadata, "source", catalog_name)
        for metadata in catalog_derived_metadata_definitions
        if is_metadata_catalog_enabled(metadata, catalog_name) and is_metadata_connector_type(metadata, "source")
    ]
    catalog_destinations = [
        metadata_to_catalog_entry(metadata, "destination", catalog_name)
        for metadata in catalog_derived_metadata_definitions
        if is_metadata_catalog_enabled(metadata, catalog_name) and is_metadata_connector_type(metadata, "destination")
    ]

    catalog = {"sources": catalog_sources, "destinations": catalog_destinations}

    return catalog


# ASSETS


@asset(group_name=GROUP_NAME)
def cloud_catalog_from_metadata(catalog_derived_metadata_definitions: List[PartialMetadataDefinition]) -> dict:
    """
    This asset is used to generate the cloud catalog from the metadata definitions.

    TODO (ben): This asset should be updated to use the GCS metadata definitions once available.
    """
    return construct_catalog_from_metadata(catalog_derived_metadata_definitions, "cloud")


@asset(group_name=GROUP_NAME)
def oss_catalog_from_metadata(catalog_derived_metadata_definitions: List[PartialMetadataDefinition]) -> dict:
    """
    This asset is used to generate the oss catalog from the metadata definitions.

    TODO (ben): This asset should be updated to use the GCS metadata definitions once available.
    """
    return construct_catalog_from_metadata(catalog_derived_metadata_definitions, "oss")


@asset(group_name=GROUP_NAME)
def cloud_sources_dataframe(latest_cloud_catalog_dict: dict) -> OutputDataFrame:
    sources = latest_cloud_catalog_dict["sources"]
    return output_dataframe(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def oss_sources_dataframe(latest_oss_catalog_dict: dict) -> OutputDataFrame:
    sources = latest_oss_catalog_dict["sources"]
    return output_dataframe(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def cloud_destinations_dataframe(latest_cloud_catalog_dict: dict) -> OutputDataFrame:
    destinations = latest_cloud_catalog_dict["destinations"]
    return output_dataframe(pd.DataFrame(destinations))


@asset(group_name=GROUP_NAME)
def oss_destinations_dataframe(latest_oss_catalog_dict: dict) -> OutputDataFrame:
    destinations = latest_oss_catalog_dict["destinations"]
    return output_dataframe(pd.DataFrame(destinations))


@asset(required_resource_keys={"latest_cloud_catalog_gcs_file"}, group_name=GROUP_NAME)
def latest_cloud_catalog_dict(context: OpExecutionContext) -> dict:
    oss_catalog_file = context.resources.latest_cloud_catalog_gcs_file
    json_string = oss_catalog_file.download_as_string().decode("utf-8")
    oss_catalog_dict = json.loads(json_string)
    return oss_catalog_dict


@asset(required_resource_keys={"latest_oss_catalog_gcs_file"}, group_name=GROUP_NAME)
def latest_oss_catalog_dict(context: OpExecutionContext) -> dict:
    oss_catalog_file = context.resources.latest_oss_catalog_gcs_file
    json_string = oss_catalog_file.download_as_string().decode("utf-8")
    oss_catalog_dict = json.loads(json_string)
    return oss_catalog_dict
