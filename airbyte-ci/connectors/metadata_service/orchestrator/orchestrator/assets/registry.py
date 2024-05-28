#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import List

import sentry_sdk
from dagster import MetadataValue, OpExecutionContext, Output, asset
from dagster_gcp.gcs.file_manager import GCSFileHandle, GCSFileManager
from google.cloud import storage
from metadata_service.models.generated.ConnectorRegistryV0 import ConnectorRegistryV0
from metadata_service.models.transform import to_json_sanitized_dict
from orchestrator.assets.registry_entry import ConnectorTypePrimaryKey, ConnectorTypes, read_registry_entry_blob
from orchestrator.logging import sentry
from orchestrator.logging.publish_connector_lifecycle import PublishConnectorLifecycle, PublishConnectorLifecycleStage, StageStatus
from orchestrator.utils.object_helpers import default_none_to_dict
from pydash.objects import set_with

GROUP_NAME = "registry"


def _get_registry_entry_id(registry_entry: dict, connector_type: ConnectorTypes) -> str:
    """Get the registry entry ID.

    A function is needed to get the registry entry ID because the primary key field is different for each connector type.

    e.g. for sources, the primary key field is "sourceDefinitionId", and for destinations, the primary key field is "destinationDefinitionId".

    Args:
        registry_entry (dict): The registry entry.
        connector_type (ConnectorTypes): The connector type.

    Returns:
        str: The registry entry ID.
    """
    pk_field = ConnectorTypePrimaryKey[connector_type.value]
    return registry_entry[pk_field]


@sentry_sdk.trace
def apply_metrics_to_registry_entry(registry_entry_dict: dict, connector_type: ConnectorTypes, latest_metrics_dict: dict) -> dict:
    """Apply the metrics to the registry entry.

    Args:
        registry_entry_dict (dict): The registry entry.
        latest_metrics_dict (dict): The metrics.

    Returns:
        dict: The registry entry with metrics.
    """
    connector_id = _get_registry_entry_id(registry_entry_dict, connector_type)
    metrics = latest_metrics_dict.get(connector_id, {})

    # Safely add metrics to ["generated"]["metrics"], knowing that the key may not exist, or might be None
    registry_entry_dict = set_with(registry_entry_dict, "generated.metrics", metrics, default_none_to_dict)

    return registry_entry_dict


@sentry_sdk.trace
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


@sentry_sdk.trace
def generate_and_persist_registry(
    context: OpExecutionContext,
    registry_entry_file_blobs: List[storage.Blob],
    registry_directory_manager: GCSFileManager,
    registry_name: str,
    latest_connnector_metrics: dict,
) -> Output[ConnectorRegistryV0]:
    """Generate the selected registry from the metadata files, and persist it to GCS.

    Args:
        context (OpExecutionContext): The execution context.
        registry_entry_file_blobs (storage.Blob): The registry entries.

    Returns:
        Output[ConnectorRegistryV0]: The registry.
    """
    PublishConnectorLifecycle.log(
        context,
        PublishConnectorLifecycleStage.REGISTRY_GENERATION,
        StageStatus.IN_PROGRESS,
        f"Generating {registry_name} registry...",
    )

    registry_dict = {"sources": [], "destinations": []}
    for blob in registry_entry_file_blobs:
        connector_type, registry_entry = read_registry_entry_blob(blob)
        plural_connector_type = f"{connector_type}s"

        # We santiize the registry entry to ensure its in a format
        # that can be parsed by pydantic.
        registry_entry_dict = to_json_sanitized_dict(registry_entry)
        enriched_registry_entry_dict = apply_metrics_to_registry_entry(registry_entry_dict, connector_type, latest_connnector_metrics)

        registry_dict[plural_connector_type].append(enriched_registry_entry_dict)

    registry_model = ConnectorRegistryV0.parse_obj(registry_dict)

    file_handle = persist_registry_to_json(registry_model, registry_name, registry_directory_manager)

    metadata = {
        "gcs_path": MetadataValue.url(file_handle.public_url),
    }

    PublishConnectorLifecycle.log(
        context,
        PublishConnectorLifecycleStage.REGISTRY_GENERATION,
        StageStatus.SUCCESS,
        f"New {registry_name} registry available at {file_handle.public_url}",
    )

    return Output(metadata=metadata, value=registry_model)


# Registry Generation


@asset(
    required_resource_keys={"slack", "registry_directory_manager", "latest_oss_registry_entries_file_blobs", "latest_metrics_gcs_blob"},
    group_name=GROUP_NAME,
)
@sentry.instrument_asset_op
def persisted_oss_registry(context: OpExecutionContext, latest_connnector_metrics: dict) -> Output[ConnectorRegistryV0]:
    """
    This asset is used to generate the oss registry from the registry entries.
    """
    registry_name = "oss"
    registry_directory_manager = context.resources.registry_directory_manager
    latest_oss_registry_entries_file_blobs = context.resources.latest_oss_registry_entries_file_blobs

    return generate_and_persist_registry(
        context=context,
        registry_entry_file_blobs=latest_oss_registry_entries_file_blobs,
        registry_directory_manager=registry_directory_manager,
        registry_name=registry_name,
        latest_connnector_metrics=latest_connnector_metrics,
    )


@asset(
    required_resource_keys={"slack", "registry_directory_manager", "latest_cloud_registry_entries_file_blobs", "latest_metrics_gcs_blob"},
    group_name=GROUP_NAME,
)
@sentry.instrument_asset_op
def persisted_cloud_registry(context: OpExecutionContext, latest_connnector_metrics: dict) -> Output[ConnectorRegistryV0]:
    """
    This asset is used to generate the cloud registry from the registry entries.
    """
    registry_name = "cloud"
    registry_directory_manager = context.resources.registry_directory_manager
    latest_cloud_registry_entries_file_blobs = context.resources.latest_cloud_registry_entries_file_blobs

    return generate_and_persist_registry(
        context=context,
        registry_entry_file_blobs=latest_cloud_registry_entries_file_blobs,
        registry_directory_manager=registry_directory_manager,
        registry_name=registry_name,
        latest_connnector_metrics=latest_connnector_metrics,
    )


# Registry from JSON


@asset(required_resource_keys={"latest_cloud_registry_gcs_blob"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def latest_cloud_registry(_context: OpExecutionContext, latest_cloud_registry_dict: dict) -> ConnectorRegistryV0:
    return ConnectorRegistryV0.parse_obj(latest_cloud_registry_dict)


@asset(required_resource_keys={"latest_oss_registry_gcs_blob"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def latest_oss_registry(_context: OpExecutionContext, latest_oss_registry_dict: dict) -> ConnectorRegistryV0:
    return ConnectorRegistryV0.parse_obj(latest_oss_registry_dict)


@asset(required_resource_keys={"latest_cloud_registry_gcs_blob"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def latest_cloud_registry_dict(context: OpExecutionContext) -> dict:
    oss_registry_file = context.resources.latest_cloud_registry_gcs_blob
    json_string = oss_registry_file.download_as_string().decode("utf-8")
    oss_registry_dict = json.loads(json_string)
    return oss_registry_dict


@asset(required_resource_keys={"latest_oss_registry_gcs_blob"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def latest_oss_registry_dict(context: OpExecutionContext) -> dict:
    oss_registry_file = context.resources.latest_oss_registry_gcs_blob
    json_string = oss_registry_file.download_as_string().decode("utf-8")
    oss_registry_dict = json.loads(json_string)
    return oss_registry_dict
