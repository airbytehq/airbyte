import pandas as pd
import json
from dagster import asset, Output, OpExecutionContext
from typing import List
from pydash.collections import key_by

from ..utils.dagster_helpers import OutputDataFrame
from deepdiff import DeepDiff


GROUP_NAME = "catalog"

# HELPERS

def metadata_to_catalog_entry(metadata_definition, connector_type):
    metadata_data = metadata_definition["data"]

    # remove the metadata fields that were added
    del metadata_data["catalogs"]

    # remove connectorType field
    del metadata_data["connectorType"]

    # rename field connectionType to sourceType
    connection_type = metadata_data.get("connectionType")
    if connection_type:
        metadata_data["sourceType"] = metadata_data["connectionType"]
        del metadata_data["connectionType"]

    # rename supportUrl to documentationUrl
    support_url = metadata_data.get("supportUrl")
    if support_url:
        metadata_data["documentationUrl"] = metadata_data["supportUrl"]
        del metadata_data["supportUrl"]

    # rename definitionId field to sourceDefinitionId or destinationDefinitionId
    id_field = "sourceDefinitionId" if connector_type == "source" else "destinationDefinitionId"
    metadata_data[id_field] = metadata_data["definitionId"]
    del metadata_data["definitionId"]

    # add in useless fields that are currently required for porting to the actor definition spec
    metadata_data["tombstone"] = False
    metadata_data["custom"] = False
    metadata_data["public"] = True

    return metadata_data

def key_catalog_entries(catalog_dict):
    catalog_dict_keyed = catalog_dict.copy()
    for connector_type, id_field in [["sources", "sourceDefinitionId"], ["destinations", "destinationDefinitionId"]]:
        catalog_dict_keyed[connector_type] = key_by(catalog_dict_keyed[connector_type], id_field)
    return catalog_dict_keyed

def diff_catalogs(catalog_dict_1, catalog_dict_2):
    excludedRegex = [
        r"githubIssueLabel",
        r"license",
        r"spec", # TODO (ben) remove this when checking the final catalog from GCS metadata
    ]
    keyed_catalog_dict_1 = key_catalog_entries(catalog_dict_1)
    keyed_catalog_dict_2 = key_catalog_entries(catalog_dict_2)

    diff = DeepDiff(keyed_catalog_dict_1, keyed_catalog_dict_2, ignore_order=True, exclude_regex_paths=excludedRegex)

    return diff

# ASSETS

@asset(group_name=GROUP_NAME)
def oss_catalog_dif(oss_catalog_from_metadata: dict, latest_oss_catalog_dict: dict):
    diff = diff_catalogs(latest_oss_catalog_dict, oss_catalog_from_metadata)
    diff_df = pd.DataFrame.from_dict(diff)

    return OutputDataFrame(diff_df)

@asset(group_name=GROUP_NAME)
def oss_catalog_from_metadata(catalog_derived_metadata_definitions):
    # get only definitions with data.catalogs.oss.enabled = true
    oss_definitions = [metadata for metadata in catalog_derived_metadata_definitions if metadata["data"]["catalogs"]["oss"]["enabled"]]

    oss_metadata_sources = [metadata for metadata in oss_definitions if metadata["data"]["connectorType"] == "source"]
    oss_metadata_destinations = [metadata for metadata in oss_definitions if metadata["data"]["connectorType"] == "destination"]

    oss_catalog_sources = [metadata_to_catalog_entry(metadata, "source") for metadata in oss_metadata_sources]
    oss_catalog_destinations = [metadata_to_catalog_entry(metadata, "destination") for metadata in oss_metadata_destinations]

    oss_catalog = {
        "sources": oss_catalog_sources,
        "destinations": oss_catalog_destinations
    }

    return oss_catalog


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
