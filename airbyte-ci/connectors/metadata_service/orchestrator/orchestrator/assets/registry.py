#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import copy
from typing import List

import pandas as pd
from dagster import asset, OpExecutionContext, MetadataValue, Output

from metadata_service.spec_cache import get_cached_spec

from orchestrator.models.metadata import MetadataDefinition
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe
from orchestrator.utils.object_helpers import deep_copy_params, to_json_sanitized_dict

from dagster_gcp.gcs.file_manager import GCSFileManager, GCSFileHandle

from metadata_service.models.generated.ConnectorRegistryV0 import ConnectorRegistryV0


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

    # remove any None values from the override registry
    override_registry = {k: v for k, v in override_registry.items() if v is not None}

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


def construct_registry_from_metadata(
    legacy_registry_derived_metadata_definitions: List[MetadataDefinition], registry_name: str
) -> ConnectorRegistryV0:
    """Construct the registry from the metadata definitions.

    Args:
        legacy_registry_derived_metadata_definitions (List[dict]): Metadata definitions that have been derived from the existing registry.
        registry_name (str): The name of the registry to construct. One of "cloud" or "oss".

    Returns:
        dict: The registry.
    """
    registry_derived_metadata_dicts = [metadata_definition.dict() for metadata_definition in legacy_registry_derived_metadata_definitions]
    registry_sources = [
        metadata_to_registry_entry(metadata, "source", registry_name)
        for metadata in registry_derived_metadata_dicts
        if is_metadata_registry_enabled(metadata, registry_name) and is_metadata_connector_type(metadata, "source")
    ]
    registry_destinations = [
        metadata_to_registry_entry(metadata, "destination", registry_name)
        for metadata in registry_derived_metadata_dicts
        if is_metadata_registry_enabled(metadata, registry_name) and is_metadata_connector_type(metadata, "destination")
    ]

    return {"sources": registry_sources, "destinations": registry_destinations}


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
            raise MissingCachedSpecError(f"No cached spec found for {entry['dockerRepository']}:{entry['dockerImageTag']}")
    return registry_with_specs


def persist_registry_to_json(
    registry: ConnectorRegistryV0, registry_name: str, registry_directory_manager: GCSFileManager
) -> GCSFileHandle:
    """Persist the registry to a json file on GCS bucket

    Args:
        registry (ConnectorRegistryV0): The registry.
        registry_name (str): The name of the registry. One of "cloud" or "oss".
        registry_directory_manager (OutputDataFrame): The registry directory manager.

    Returns:
        OutputDataFrame: The registry directory manager.
    """
    registry_file_name = f"{registry_name}_registry"
    registry_json = registry.json()
    file_handle = registry_directory_manager.write_data(registry_json.encode("utf-8"), ext="json", key=registry_file_name)
    return file_handle


def generate_and_persist_registry(
    metadata_definitions: List[MetadataDefinition],
    cached_specs: OutputDataFrame,
    registry_directory_manager: GCSFileManager,
    registry_name: str,
) -> Output[ConnectorRegistryV0]:
    """Generate the selected registry from the metadata files, and persist it to GCS.

    Args:
        context (OpExecutionContext): The execution context.
        metadata_definitions (List[MetadataDefinition]): The metadata definitions.
        cached_specs (OutputDataFrame): The cached specs.

    Returns:
        Output[ConnectorRegistryV0]: The registry.
    """

    from_metadata = construct_registry_from_metadata(metadata_definitions, registry_name)
    registry_dict = construct_registry_with_spec_from_registry(from_metadata, cached_specs)
    registry_model = ConnectorRegistryV0.parse_obj(registry_dict)

    file_handle = persist_registry_to_json(registry_model, registry_name, registry_directory_manager)

    metadata = {
        "gcs_path": MetadataValue.url(file_handle.gcs_path),
    }

    return Output(metadata=metadata, value=registry_model)


# New Registry


@asset(required_resource_keys={"registry_directory_manager"}, group_name=GROUP_NAME)
def cloud_registry_from_metadata(
    context: OpExecutionContext, metadata_definitions: List[MetadataDefinition], cached_specs: OutputDataFrame
) -> Output[ConnectorRegistryV0]:
    """
    This asset is used to generate the cloud registry from the metadata definitions.
    """
    registry_name = "cloud"
    registry_directory_manager = context.resources.registry_directory_manager

    return generate_and_persist_registry(
        metadata_definitions=metadata_definitions,
        cached_specs=cached_specs,
        registry_directory_manager=registry_directory_manager,
        registry_name=registry_name,
    )


@asset(required_resource_keys={"registry_directory_manager"}, group_name=GROUP_NAME)
def oss_registry_from_metadata(
    context: OpExecutionContext, metadata_definitions: List[MetadataDefinition], cached_specs: OutputDataFrame
) -> Output[ConnectorRegistryV0]:
    """
    This asset is used to generate the oss registry from the metadata definitions.
    """
    registry_name = "oss"
    registry_directory_manager = context.resources.registry_directory_manager

    return generate_and_persist_registry(
        metadata_definitions=metadata_definitions,
        cached_specs=cached_specs,
        registry_directory_manager=registry_directory_manager,
        registry_name=registry_name,
    )


@asset(group_name=GROUP_NAME)
def cloud_sources_dataframe(cloud_registry_from_metadata: ConnectorRegistryV0) -> OutputDataFrame:
    cloud_registry_from_metadata_dict = to_json_sanitized_dict(cloud_registry_from_metadata)
    sources = cloud_registry_from_metadata_dict["sources"]
    return output_dataframe(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def oss_sources_dataframe(oss_registry_from_metadata: ConnectorRegistryV0) -> OutputDataFrame:
    oss_registry_from_metadata_dict = to_json_sanitized_dict(oss_registry_from_metadata)
    sources = oss_registry_from_metadata_dict["sources"]
    return output_dataframe(pd.DataFrame(sources))


@asset(group_name=GROUP_NAME)
def cloud_destinations_dataframe(cloud_registry_from_metadata: ConnectorRegistryV0) -> OutputDataFrame:
    cloud_registry_from_metadata_dict = to_json_sanitized_dict(cloud_registry_from_metadata)
    destinations = cloud_registry_from_metadata_dict["destinations"]
    return output_dataframe(pd.DataFrame(destinations))


@asset(group_name=GROUP_NAME)
def oss_destinations_dataframe(oss_registry_from_metadata: ConnectorRegistryV0) -> OutputDataFrame:
    oss_registry_from_metadata_dict = to_json_sanitized_dict(oss_registry_from_metadata)
    destinations = oss_registry_from_metadata_dict["destinations"]
    return output_dataframe(pd.DataFrame(destinations))
