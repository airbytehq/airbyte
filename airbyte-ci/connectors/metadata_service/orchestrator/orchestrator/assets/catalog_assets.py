import pandas as pd
import json
from dagster import asset, OpExecutionContext
from typing import List

from ..utils.dagster_helpers import OutputDataFrame


GROUP_NAME = "catalog"

# HELPERS


def apply_overrides_from_catalog(metadata_data: dict, override_catalog: str) -> dict:
    catalog_fields = metadata_data["catalogs"][override_catalog]
    del catalog_fields["enabled"]
    for field, value in catalog_fields.items():
        metadata_data[field] = value
    return metadata_data


def metadata_to_catalog_entry(metadata_definition: dict, connector_type: str, override_catalog: str) -> dict:
    metadata_data = metadata_definition["data"]

    # remove the metadata fields that were added
    overrode_metadata_data = apply_overrides_from_catalog(metadata_data, override_catalog)
    del overrode_metadata_data["catalogs"]

    # remove connectorType field
    del overrode_metadata_data["connectorType"]

    # rename field connectionType to sourceType
    connection_type = overrode_metadata_data.get("connectionType")
    if connection_type:
        overrode_metadata_data["sourceType"] = overrode_metadata_data["connectionType"]
        del overrode_metadata_data["connectionType"]

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


def construct_catalog_from_metadata(catalog_derived_metadata_definitions: List[dict], catalog_name: str) -> dict:
    # get only definitions with data.catalogs.cloud.enabled = true
    metadata_definitions = [
        metadata for metadata in catalog_derived_metadata_definitions if metadata["data"]["catalogs"][catalog_name]["enabled"]
    ]

    metadata_sources = [metadata for metadata in metadata_definitions if metadata["data"]["connectorType"] == "source"]
    metadata_destinations = [metadata for metadata in metadata_definitions if metadata["data"]["connectorType"] == "destination"]

    catalog_sources = [
        metadata_to_catalog_entry(
            metadata,
            "source",
            catalog_name,
        )
        for metadata in metadata_sources
    ]
    catalog_destinations = [metadata_to_catalog_entry(metadata, "destination", catalog_name) for metadata in metadata_destinations]

    catalog = {"sources": catalog_sources, "destinations": catalog_destinations}

    return catalog


# ASSETS


@asset(group_name=GROUP_NAME)
def cloud_catalog_from_metadata(catalog_derived_metadata_definitions: List[dict]) -> dict:
    """
    This asset is used to generate the cloud catalog from the metadata definitions.

    TODO (ben): This asset should be updated to use the GCS metadata definitions once available.
    """
    return construct_catalog_from_metadata(catalog_derived_metadata_definitions, "cloud")


@asset(group_name=GROUP_NAME)
def oss_catalog_from_metadata(catalog_derived_metadata_definitions: List[dict]) -> dict:
    """
    This asset is used to generate the oss catalog from the metadata definitions.

    TODO (ben): This asset should be updated to use the GCS metadata definitions once available.
    """
    return construct_catalog_from_metadata(catalog_derived_metadata_definitions, "oss")


@asset(group_name=GROUP_NAME)
def cloud_sources_dataframe(latest_cloud_catalog_dict: dict):
    sources = latest_cloud_catalog_dict["sources"]
    return OutputDataFrame(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def oss_sources_dataframe(latest_oss_catalog_dict: dict):
    sources = latest_oss_catalog_dict["sources"]
    return OutputDataFrame(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def cloud_destinations_dataframe(latest_cloud_catalog_dict: dict):
    destinations = latest_cloud_catalog_dict["destinations"]
    return OutputDataFrame(pd.DataFrame(destinations))


@asset(group_name=GROUP_NAME)
def oss_destinations_dataframe(latest_oss_catalog_dict: dict):
    destinations = latest_oss_catalog_dict["destinations"]
    return OutputDataFrame(pd.DataFrame(destinations))


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
