#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import copy
import json
from typing import List

import pandas as pd
from dagster import OpExecutionContext, asset
from metadata_service.spec_cache import get_cached_spec
from orchestrator.models.metadata import PartialMetadataDefinition
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe
from orchestrator.utils.object_helpers import deep_copy_params

GROUP_NAME = "registry"

# ERRORS


class MissingCachedSpecError(Exception):
    pass


# HELPERS


@deep_copy_params
def apply_overrides_from_registry(metadata_data: dict, override_registry_key: str) -> dict:
    """Apply the overrides from the registry to the metadata data.

    Args:
        metadata_data (dict): The metadata data field.
        override_registry_key (str): The key of the registry to override the metadata with.

    Returns:
        dict: The metadata data field with the overrides applied.
    """
    override_registry = metadata_data["registries"][override_registry_key]
    del override_registry["enabled"]
    metadata_data.update(override_registry)

    return metadata_data


@deep_copy_params
def metadata_to_registry_entry(metadata_definition: dict, connector_type: str, override_registry_key: str) -> dict:
    """Convert the metadata definition to a registry entry.

    Args:
        metadata_definition (dict): The metadata definition.
        connector_type (str): One of "source" or "destination".
        override_registry_key (str): The key of the registry to override the metadata with.

    Returns:
        dict: The registry equivalent of the metadata definition.
    """
    metadata_data = metadata_definition["data"]

    overrode_metadata_data = apply_overrides_from_registry(metadata_data, override_registry_key)
    del overrode_metadata_data["registries"]

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
    # Note: this is something our current cloud registry generator does
    # Note: We will not once this is live
    if not overrode_metadata_data.get("releaseStage"):
        overrode_metadata_data["releaseStage"] = "alpha"

    return overrode_metadata_data


def is_metadata_registry_enabled(metadata_definition: dict, registry_name: str) -> bool:
    return metadata_definition["data"]["registries"][registry_name]["enabled"]


def is_metadata_connector_type(metadata_definition: dict, connector_type: str) -> bool:
    return metadata_definition["data"]["connectorType"] == connector_type


def construct_registry_from_metadata(registry_derived_metadata_definitions: List[PartialMetadataDefinition], registry_name: str) -> dict:
    """Construct the registry from the metadata definitions.

    Args:
        registry_derived_metadata_definitions (List[dict]): Metadata definitions that have been derived from the existing registry.
        registry_name (str): The name of the registry to construct. One of "cloud" or "oss".

    Returns:
        dict: The registry.
    """
    registry_sources = [
        metadata_to_registry_entry(metadata, "source", registry_name)
        for metadata in registry_derived_metadata_definitions
        if is_metadata_registry_enabled(metadata, registry_name) and is_metadata_connector_type(metadata, "source")
    ]
    registry_destinations = [
        metadata_to_registry_entry(metadata, "destination", registry_name)
        for metadata in registry_derived_metadata_definitions
        if is_metadata_registry_enabled(metadata, registry_name) and is_metadata_connector_type(metadata, "destination")
    ]

    registry = {"sources": registry_sources, "destinations": registry_destinations}

    return registry


def construct_registry_with_spec_from_registry(registry: dict, cached_specs: OutputDataFrame) -> dict:
    entries = [("source", entry) for entry in registry["sources"]] + [("destinations", entry) for entry in registry["destinations"]]

    cached_connector_version = {
        (cached_spec["docker_repository"], cached_spec["docker_image_tag"]): cached_spec["spec_cache_path"]
        for cached_spec in cached_specs.to_dict(orient="records")
    }
    registry_with_specs = {"sources": [], "destinations": []}
    for connector_type, entry in entries:
        try:
            spec_path = cached_connector_version[(entry["dockerRepository"], entry["dockerImageTag"])]
            entry_with_spec = copy.deepcopy(entry)
            entry_with_spec["spec"] = get_cached_spec(spec_path)
            if connector_type == "source":
                registry_with_specs["sources"].append(entry_with_spec)
            else:
                registry_with_specs["destinations"].append(entry_with_spec)
        except KeyError:
            raise MissingCachedSpecError(f"No cached spec found for {entry['dockerRegistry']:{entry['dockerImageTag']}}")
    return registry_with_specs


# ASSETS


@asset(group_name=GROUP_NAME)
def cloud_registry_from_metadata(
    registry_derived_metadata_definitions: List[PartialMetadataDefinition], cached_specs: OutputDataFrame
) -> dict:
    """
    This asset is used to generate the cloud registry from the metadata definitions.

    TODO (ben): This asset should be updated to use the GCS metadata definitions once available.
    """
    from_metadata = construct_registry_from_metadata(registry_derived_metadata_definitions, "cloud")
    from_metadata_and_spec = construct_registry_with_spec_from_registry(from_metadata, cached_specs)
    return from_metadata_and_spec


@asset(group_name=GROUP_NAME)
def oss_registry_from_metadata(registry_derived_metadata_definitions: List[PartialMetadataDefinition], cached_specs: OutputDataFrame) -> dict:
    """
    This asset is used to generate the oss registry from the metadata definitions.

    TODO (ben): This asset should be updated to use the GCS metadata definitions once available.
    """
    from_metadata = construct_registry_from_metadata(registry_derived_metadata_definitions, "oss")
    from_metadata_and_spec = construct_registry_with_spec_from_registry(from_metadata, cached_specs)
    return from_metadata_and_spec


@asset(group_name=GROUP_NAME)
def cloud_sources_dataframe(latest_cloud_registry_dict: dict) -> OutputDataFrame:
    sources = latest_cloud_registry_dict["sources"]
    return output_dataframe(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def oss_sources_dataframe(latest_oss_registry_dict: dict) -> OutputDataFrame:
    sources = latest_oss_registry_dict["sources"]
    return output_dataframe(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def cloud_destinations_dataframe(latest_cloud_registry_dict: dict) -> OutputDataFrame:
    destinations = latest_cloud_registry_dict["destinations"]
    return output_dataframe(pd.DataFrame(destinations))


@asset(group_name=GROUP_NAME)
def oss_destinations_dataframe(latest_oss_registry_dict: dict) -> OutputDataFrame:
    destinations = latest_oss_registry_dict["destinations"]
    return output_dataframe(pd.DataFrame(destinations))


@asset(required_resource_keys={"latest_cloud_registry_gcs_file"}, group_name=GROUP_NAME)
def latest_cloud_registry_dict(context: OpExecutionContext) -> dict:
    oss_registry_file = context.resources.latest_cloud_registry_gcs_file
    json_string = oss_registry_file.download_as_string().decode("utf-8")
    oss_registry_dict = json.loads(json_string)
    return oss_registry_dict


@asset(required_resource_keys={"latest_oss_registry_gcs_file"}, group_name=GROUP_NAME)
def latest_oss_registry_dict(context: OpExecutionContext) -> dict:
    oss_registry_file = context.resources.latest_oss_registry_gcs_file
    json_string = oss_registry_file.download_as_string().decode("utf-8")
    oss_registry_dict = json.loads(json_string)
    return oss_registry_dict
