#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
from google.cloud import storage

from dagster import asset, OpExecutionContext, MetadataValue, Output
from dagster_gcp.gcs.file_manager import GCSFileManager, GCSFileHandle

from metadata_service.models.generated.ConnectorRegistryV0 import ConnectorRegistryV0
from orchestrator.assets.registry_entry import read_registry_entry_blob
from orchestrator.utils.object_helpers import to_json_sanitized_dict

from typing import List


GROUP_NAME = "registry"


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
    registry_entry_file_blobs: List[storage.Blob],
    registry_directory_manager: GCSFileManager,
    registry_name: str,
) -> Output[ConnectorRegistryV0]:
    """Generate the selected registry from the metadata files, and persist it to GCS.

    Args:
        context (OpExecutionContext): The execution context.
        registry_entry_file_blobs (storage.Blob): The registry entries.

    Returns:
        Output[ConnectorRegistryV0]: The registry.
    """
    registry_dict = {"sources": [], "destinations": []}
    for blob in registry_entry_file_blobs:
        registry_entry, connector_type = read_registry_entry_blob(blob)
        plural_connector_type = f"{connector_type}s"

        # We santiize the registry entry to ensure its in a format
        # that can be parsed by pydantic.
        registry_entry_dict = to_json_sanitized_dict(registry_entry)

        registry_dict[plural_connector_type].append(registry_entry_dict)

    registry_model = ConnectorRegistryV0.parse_obj(registry_dict)

    file_handle = persist_registry_to_json(registry_model, registry_name, registry_directory_manager)

    metadata = {
        "gcs_path": MetadataValue.url(file_handle.public_url),
    }

    return Output(metadata=metadata, value=registry_model)


# Registry Generation


@asset(required_resource_keys={"registry_directory_manager", "latest_oss_registry_entries_file_blobs"}, group_name=GROUP_NAME)
def persisted_oss_registry(context: OpExecutionContext) -> Output[ConnectorRegistryV0]:
    """
    This asset is used to generate the oss registry from the registry entries.
    """
    registry_name = "oss"
    registry_directory_manager = context.resources.registry_directory_manager
    latest_oss_registry_entries_file_blobs = context.resources.latest_oss_registry_entries_file_blobs

    return generate_and_persist_registry(
        registry_entry_file_blobs=latest_oss_registry_entries_file_blobs,
        registry_directory_manager=registry_directory_manager,
        registry_name=registry_name,
    )


@asset(required_resource_keys={"registry_directory_manager", "latest_cloud_registry_entries_file_blobs"}, group_name=GROUP_NAME)
def persisted_cloud_registry(context: OpExecutionContext) -> Output[ConnectorRegistryV0]:
    """
    This asset is used to generate the cloud registry from the registry entries.
    """
    registry_name = "cloud"
    registry_directory_manager = context.resources.registry_directory_manager
    latest_cloud_registry_entries_file_blobs = context.resources.latest_cloud_registry_entries_file_blobs

    return generate_and_persist_registry(
        registry_entry_file_blobs=latest_cloud_registry_entries_file_blobs,
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
