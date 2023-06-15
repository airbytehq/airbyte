#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import copy
import json
from typing import List, Optional
from pydash.objects import get

import pandas as pd
from dagster import asset, OpExecutionContext, MetadataValue, Output

from metadata_service.spec_cache import get_cached_spec

from orchestrator.models.metadata import LatestMetadataEntry
from orchestrator.utils.dagster_helpers import OutputDataFrame
from orchestrator.utils.object_helpers import deep_copy_params

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


def calculate_migration_documentation_url(releases_or_breaking_change: dict, documentation_url: str, version: Optional[str] = None) -> str:
    """Calculate the migration documentation url for the connector releases.

    Args:
        metadata_releases (dict): The connector releases.

    Returns:
        str: The migration documentation url.
    """

    base_url = f"{documentation_url}/migration_guide"
    default_migration_documentation_url = f"{base_url}#{version}" if version is not None else base_url

    return releases_or_breaking_change.get("migrationDocumentationUrl", default_migration_documentation_url)


@deep_copy_params
def apply_connector_release_defaults(metadata: dict) -> Optional[pd.DataFrame]:
    metadata_releases = metadata.get("releases")
    documentation_url = metadata.get("documentationUrl")
    if metadata_releases is None:
        return None

    # apply defaults for connector releases
    metadata_releases["migrationDocumentationUrl"] = calculate_migration_documentation_url(metadata_releases, documentation_url)

    # releases has a dictionary field called breakingChanges, where the key is the version and the value is the data for the breaking change
    # each breaking change has a migrationDocumentationUrl field that is optional, so we need to apply defaults to it
    breaking_changes = metadata_releases["breakingChanges"]
    if breaking_changes is not None:
        for version, breaking_change in breaking_changes.items():
            breaking_change["migrationDocumentationUrl"] = calculate_migration_documentation_url(
                breaking_change, documentation_url, version
            )

    return metadata_releases


@deep_copy_params
def metadata_to_registry_entry(metadata_entry: LatestMetadataEntry, connector_type: str, override_registry_key: str) -> dict:
    """Convert the metadata definition to a registry entry.

    Args:
        metadata_definition (dict): The metadata definition.
        connector_type (str): One of "source" or "destination".
        override_registry_key (str): The key of the registry to override the metadata with.

    Returns:
        dict: The registry equivalent of the metadata definition.
    """
    metadata_definition = metadata_entry.metadata_definition.dict()

    metadata_data = metadata_definition["data"]

    # apply overrides from the registry
    overrode_metadata_data = apply_overrides_from_registry(metadata_data, override_registry_key)

    # remove fields that are not needed in the registry
    del overrode_metadata_data["registries"]
    del overrode_metadata_data["connectorType"]

    # rename field connectorSubtype to sourceType
    connection_type = overrode_metadata_data.get("connectorSubtype")
    if connection_type:
        overrode_metadata_data["sourceType"] = overrode_metadata_data["connectorSubtype"]
        del overrode_metadata_data["connectorSubtype"]

    # rename definitionId field to sourceDefinitionId or destinationDefinitionId
    id_field = "sourceDefinitionId" if connector_type == "source" else "destinationDefinitionId"
    overrode_metadata_data[id_field] = overrode_metadata_data["definitionId"]
    del overrode_metadata_data["definitionId"]

    # add in useless fields that are currently required for porting to the actor definition spec
    overrode_metadata_data["tombstone"] = False
    overrode_metadata_data["custom"] = False
    overrode_metadata_data["public"] = True

    # if there is no releaseStage, set it to "alpha"
    if not overrode_metadata_data.get("releaseStage"):
        overrode_metadata_data["releaseStage"] = "alpha"

    # apply generated fields
    overrode_metadata_data["iconUrl"] = metadata_entry.icon_url
    overrode_metadata_data["releases"] = apply_connector_release_defaults(overrode_metadata_data)

    return overrode_metadata_data


def is_metadata_registry_enabled(metadata_entry: LatestMetadataEntry, registry_name: str) -> bool:
    metadata_definition = metadata_entry.metadata_definition.dict()
    return get(metadata_definition, f"data.registries.{registry_name}.enabled", False)


def is_metadata_connector_type(metadata_entry: LatestMetadataEntry, connector_type: str) -> bool:
    metadata_definition = metadata_entry.metadata_definition.dict()
    return metadata_definition["data"]["connectorType"] == connector_type


def construct_registry_from_metadata(metadata_entries: List[LatestMetadataEntry], registry_name: str) -> ConnectorRegistryV0:
    """Construct the registry from the metadata definitions.

    Args:
        metadata_entries (List[dict]): Metadata definitions that have been derived from the existing registry.
        registry_name (str): The name of the registry to construct. One of "cloud" or "oss".

    Returns:
        dict: The registry.
    """
    registry_sources = [
        metadata_to_registry_entry(metadata_entry, "source", registry_name)
        for metadata_entry in metadata_entries
        if is_metadata_registry_enabled(metadata_entry, registry_name) and is_metadata_connector_type(metadata_entry, "source")
    ]
    registry_destinations = [
        metadata_to_registry_entry(metadata_entry, "destination", registry_name)
        for metadata_entry in metadata_entries
        if is_metadata_registry_enabled(metadata_entry, registry_name) and is_metadata_connector_type(metadata_entry, "destination")
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
    registry_json = registry.json(exclude_none=True)

    file_handle = registry_directory_manager.write_data(registry_json.encode("utf-8"), ext="json", key=registry_file_name)
    return file_handle


def generate_and_persist_registry(
    metadata_definitions: List[LatestMetadataEntry],
    cached_specs: OutputDataFrame,
    registry_directory_manager: GCSFileManager,
    registry_name: str,
) -> Output[ConnectorRegistryV0]:
    """Generate the selected registry from the metadata files, and persist it to GCS.

    Args:
        context (OpExecutionContext): The execution context.
        metadata_definitions (List[LatestMetadataEntry]): The metadata definitions.
        cached_specs (OutputDataFrame): The cached specs.

    Returns:
        Output[ConnectorRegistryV0]: The registry.
    """

    from_metadata = construct_registry_from_metadata(metadata_definitions, registry_name)
    registry_dict = construct_registry_with_spec_from_registry(from_metadata, cached_specs)
    registry_model = ConnectorRegistryV0.parse_obj(registry_dict)

    file_handle = persist_registry_to_json(registry_model, registry_name, registry_directory_manager)

    metadata = {
        "gcs_path": MetadataValue.url(file_handle.public_url),
    }

    return Output(metadata=metadata, value=registry_model)


# Registry Generation


@asset(required_resource_keys={"registry_directory_manager"}, group_name=GROUP_NAME)
def persist_cloud_registry_from_metadata(
    context: OpExecutionContext, metadata_definitions: List[LatestMetadataEntry], cached_specs: OutputDataFrame
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
def persist_oss_registry_from_metadata(
    context: OpExecutionContext, metadata_definitions: List[LatestMetadataEntry], cached_specs: OutputDataFrame
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


# Registry from JSON


@asset(required_resource_keys={"latest_cloud_registry_gcs_blob"}, group_name=GROUP_NAME)
def latest_cloud_registry(latest_cloud_registry_dict: dict) -> ConnectorRegistryV0:
    return ConnectorRegistryV0.parse_obj(latest_cloud_registry_dict)


@asset(required_resource_keys={"latest_oss_registry_gcs_blob"}, group_name=GROUP_NAME)
def latest_oss_registry(latest_oss_registry_dict: dict) -> ConnectorRegistryV0:
    return ConnectorRegistryV0.parse_obj(latest_oss_registry_dict)


@asset(required_resource_keys={"latest_cloud_registry_gcs_blob"}, group_name=GROUP_NAME)
def latest_cloud_registry_dict(context: OpExecutionContext) -> dict:
    oss_registry_file = context.resources.latest_cloud_registry_gcs_blob
    json_string = oss_registry_file.download_as_string().decode("utf-8")
    oss_registry_dict = json.loads(json_string)
    return oss_registry_dict


@asset(required_resource_keys={"latest_oss_registry_gcs_blob"}, group_name=GROUP_NAME)
def latest_oss_registry_dict(context: OpExecutionContext) -> dict:
    oss_registry_file = context.resources.latest_oss_registry_gcs_blob
    json_string = oss_registry_file.download_as_string().decode("utf-8")
    oss_registry_dict = json.loads(json_string)
    return oss_registry_dict
