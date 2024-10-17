#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
import os
from datetime import datetime
from enum import Enum
from typing import List, Optional, Tuple, Union

import orchestrator.hacks as HACKS
import pandas as pd
import semver
import sentry_sdk
from dagster import AutoMaterializePolicy, DynamicPartitionsDefinition, MetadataValue, OpExecutionContext, Output, asset
from dagster_gcp.gcs.file_manager import GCSFileHandle, GCSFileManager
from google.cloud import storage
from metadata_service.constants import ICON_FILE_NAME, METADATA_FILE_NAME
from metadata_service.models.generated.ConnectorRegistryDestinationDefinition import ConnectorRegistryDestinationDefinition
from metadata_service.models.generated.ConnectorRegistrySourceDefinition import ConnectorRegistrySourceDefinition
from metadata_service.models.transform import to_json_sanitized_dict
from metadata_service.spec_cache import SpecCache
from orchestrator.config import MAX_METADATA_PARTITION_RUN_REQUEST, VALID_REGISTRIES, get_public_url_for_gcs_file
from orchestrator.fetcher.connector_cdk_version import get_cdk_version
from orchestrator.logging import sentry
from orchestrator.logging.publish_connector_lifecycle import PublishConnectorLifecycle, PublishConnectorLifecycleStage, StageStatus
from orchestrator.models.metadata import LatestMetadataEntry, MetadataDefinition
from orchestrator.utils.blob_helpers import yaml_blob_to_dict
from orchestrator.utils.object_helpers import CaseInsensitveKeys, deep_copy_params, default_none_to_dict
from pydantic import BaseModel, ValidationError
from pydash.objects import get, set_with

GROUP_NAME = "registry_entry"

# TYPES


class ConnectorTypes(str, Enum, metaclass=CaseInsensitveKeys):
    SOURCE = "source"
    DESTINATION = "destination"


class ConnectorTypePrimaryKey(str, Enum, metaclass=CaseInsensitveKeys):
    SOURCE = "sourceDefinitionId"
    DESTINATION = "destinationDefinitionId"


PolymorphicRegistryEntry = Union[ConnectorRegistrySourceDefinition, ConnectorRegistryDestinationDefinition]
TaggedRegistryEntry = Tuple[ConnectorTypes, PolymorphicRegistryEntry]

metadata_partitions_def = DynamicPartitionsDefinition(name="metadata")

# ERRORS


class MissingCachedSpecError(Exception):
    pass


# HELPERS


@sentry_sdk.trace
def apply_spec_to_registry_entry(registry_entry: dict, spec_cache: SpecCache, registry_name: str) -> dict:
    cached_spec = spec_cache.find_spec_cache_with_fallback(
        registry_entry["dockerRepository"], registry_entry["dockerImageTag"], registry_name
    )
    if cached_spec is None:
        raise MissingCachedSpecError(f"No cached spec found for {registry_entry['dockerRepository']}:{registry_entry['dockerImageTag']}")

    entry_with_spec = copy.deepcopy(registry_entry)
    entry_with_spec["spec"] = spec_cache.download_spec(cached_spec)
    return entry_with_spec


def calculate_migration_documentation_url(releases_or_breaking_change: dict, documentation_url: str, version: Optional[str] = None) -> str:
    """Calculate the migration documentation url for the connector releases.

    Args:
        metadata_releases (dict): The connector releases.

    Returns:
        str: The migration documentation url.
    """

    base_url = f"{documentation_url}-migrations"
    default_migration_documentation_url = f"{base_url}#{version}" if version is not None else base_url

    return releases_or_breaking_change.get("migrationDocumentationUrl", None) or default_migration_documentation_url


@deep_copy_params
def apply_connector_releases(metadata: dict) -> Optional[pd.DataFrame]:
    documentation_url = metadata.get("documentationUrl")
    final_registry_releases = {}
    releases = metadata.get("releases")
    if releases is not None and releases.get("breakingChanges"):
        # apply defaults for connector releases
        final_registry_releases["migrationDocumentationUrl"] = calculate_migration_documentation_url(
            metadata["releases"], documentation_url
        )

        # releases has a dictionary field called breakingChanges, where the key is the version and the value is the data for the breaking change
        # each breaking change has a migrationDocumentationUrl field that is optional, so we need to apply defaults to it
        breaking_changes = metadata["releases"]["breakingChanges"]
        if breaking_changes is not None:
            for version, breaking_change in breaking_changes.items():
                breaking_change["migrationDocumentationUrl"] = calculate_migration_documentation_url(
                    breaking_change, documentation_url, version
                )
            final_registry_releases["breakingChanges"] = breaking_changes

    if releases is not None and releases.get("rolloutConfiguration"):
        final_registry_releases["rolloutConfiguration"] = metadata["releases"]["rolloutConfiguration"]
    return final_registry_releases


@deep_copy_params
def apply_overrides_from_registry(metadata_data: dict, override_registry_key: str) -> dict:
    """Apply the overrides from the registry to the metadata data.

    Args:
        metadata_data (dict): The metadata data field.
        override_registry_key (str): The key of the registry to override the metadata with.

    Returns:
        dict: The metadata data field with the overrides applied.
    """
    override_registry = metadata_data["registryOverrides"][override_registry_key]
    del override_registry["enabled"]

    # remove any None values from the override registry
    override_registry = {k: v for k, v in override_registry.items() if v is not None}

    metadata_data.update(override_registry)

    return metadata_data


@deep_copy_params
def apply_ab_internal_defaults(metadata_data: dict) -> dict:
    """Apply ab_internal defaults to the metadata data field.

    Args:
        metadata_data (dict): The metadata data field.

    Returns:
        dict: The metadata data field with the ab_internal defaults applied.
    """
    default_ab_internal_values = {
        "sl": 100,
        "ql": 100,
    }

    existing_ab_internal_values = metadata_data.get("ab_internal") or {}
    ab_internal_values = {**default_ab_internal_values, **existing_ab_internal_values}

    metadata_data["ab_internal"] = ab_internal_values

    return metadata_data


@deep_copy_params
def apply_generated_fields(metadata_data: dict, metadata_entry: LatestMetadataEntry) -> dict:
    """Apply generated fields to the metadata data field.

    Args:
        metadata_data (dict): The metadata data field.
        metadata_entry (LatestMetadataEntry): The metadata entry.

    Returns:
        dict: The metadata data field with the generated fields applied.
    """
    generated_fields = metadata_data.get("generated") or {}

    # Add the source file metadata
    generated_fields = set_with(generated_fields, "source_file_info.metadata_etag", metadata_entry.etag, default_none_to_dict)
    generated_fields = set_with(generated_fields, "source_file_info.metadata_file_path", metadata_entry.file_path, default_none_to_dict)
    generated_fields = set_with(generated_fields, "source_file_info.metadata_bucket_name", metadata_entry.bucket_name, default_none_to_dict)
    generated_fields = set_with(
        generated_fields, "source_file_info.metadata_last_modified", metadata_entry.last_modified, default_none_to_dict
    )

    # Add the registry entry generation timestamp
    generated_fields = set_with(
        generated_fields, "source_file_info.registry_entry_generated_at", datetime.now().isoformat(), default_none_to_dict
    )

    return generated_fields


@deep_copy_params
def apply_package_info_fields(metadata_data: dict, metadata_entry: LatestMetadataEntry) -> dict:
    """Apply package info fields to the metadata data field.

    Args:
        metadata_data (dict): The metadata data field.

    Returns:
        dict: The metadata data field with the package info fields applied.
    """
    package_info_fields = metadata_data.get("packageInfo") or {}
    package_info_fields = set_with(package_info_fields, "cdk_version", get_cdk_version(metadata_entry), default_none_to_dict)

    return package_info_fields


@deep_copy_params
def apply_language_field(metadata_data: dict) -> dict:
    """Transform the language tag into a top-level field, if it is not already present.

    Args:
        metadata_data (dict): The metadata data field.

    Returns:
        dict: The metadata data field with the language field applied.
    """
    if metadata_data.get("language"):
        return metadata_data

    tags = metadata_data.get("tags", [])
    languages = [tag.replace("language:", "") for tag in tags if tag.startswith("language:")]
    metadata_data["language"] = languages[0] if languages else None

    return metadata_data


@deep_copy_params
@sentry_sdk.trace
def metadata_to_registry_entry(metadata_entry: LatestMetadataEntry, override_registry_key: str) -> dict:
    """Convert the metadata definition to a registry entry.

    Args:
        metadata_entry (LatestMetadataEntry): The metadata definition.
        override_registry_key (str): The key of the registry to override the metadata with.

    Returns:
        dict: The registry equivalent of the metadata definition.
    """
    metadata_definition = metadata_entry.metadata_definition.dict()
    metadata_data = metadata_definition["data"]
    connector_type = metadata_data["connectorType"]

    # apply overrides from the registry
    overridden_metadata_data = apply_overrides_from_registry(metadata_data, override_registry_key)

    # remove fields that are not needed in the registry
    del overridden_metadata_data["registryOverrides"]
    del overridden_metadata_data["connectorType"]

    # rename field connectorSubtype to sourceType
    connector_subtype = overridden_metadata_data.get("connectorSubtype")
    if connector_subtype:
        overridden_metadata_data["sourceType"] = overridden_metadata_data["connectorSubtype"]
        del overridden_metadata_data["connectorSubtype"]

    # rename definitionId field to sourceDefinitionId or destinationDefinitionId
    id_field = "sourceDefinitionId" if connector_type == "source" else "destinationDefinitionId"
    overridden_metadata_data[id_field] = overridden_metadata_data["definitionId"]
    del overridden_metadata_data["definitionId"]

    # add in useless fields that are currently required for porting to the actor definition spec
    overridden_metadata_data["tombstone"] = False
    overridden_metadata_data["custom"] = False
    overridden_metadata_data["public"] = True

    # Add generated fields for source file metadata and git
    overridden_metadata_data["generated"] = apply_generated_fields(overridden_metadata_data, metadata_entry)

    # Add Dependency information
    overridden_metadata_data["packageInfo"] = apply_package_info_fields(overridden_metadata_data, metadata_entry)

    # Add language field
    overridden_metadata_data = apply_language_field(overridden_metadata_data)

    # if there is no supportLevel, set it to "community"
    if not overridden_metadata_data.get("supportLevel"):
        overridden_metadata_data["supportLevel"] = "community"

    # apply ab_internal defaults
    overridden_metadata_data = apply_ab_internal_defaults(overridden_metadata_data)

    # apply generated fields
    overridden_metadata_data["iconUrl"] = metadata_entry.icon_url
    overridden_metadata_data["releases"] = apply_connector_releases(overridden_metadata_data)
    return overridden_metadata_data


def apply_entry_schema_migrations(registry_entry: dict) -> dict:
    """Apply schema migrations to the registry entry.

    Args:
        registry_entry (dict): The registry entry.

    Returns:
        dict: The registry entry with the schema migrations applied.
    """
    # Remove the isReleaseCandidate field from the registry entry
    if registry_entry.get("releases", {}).get("isReleaseCandidate") is not None:
        registry_entry["releases"].pop("isReleaseCandidate")
    # Remove the releases field if it is empty
    if registry_entry.get("releases") == dict():
        registry_entry.pop("releases")
    return registry_entry


@sentry_sdk.trace
def read_registry_entry_blob(registry_entry_blob: storage.Blob) -> TaggedRegistryEntry:
    json_string = registry_entry_blob.download_as_string().decode("utf-8")
    registry_entry_dict = json.loads(json_string)

    connector_type, ConnectorModel = get_connector_type_from_registry_entry(registry_entry_dict)
    registry_entry_dict = apply_entry_schema_migrations(registry_entry_dict)
    registry_entry = ConnectorModel.parse_obj(registry_entry_dict)

    return connector_type, registry_entry


def get_connector_type_from_registry_entry(registry_entry: dict) -> TaggedRegistryEntry:
    if registry_entry.get(ConnectorTypePrimaryKey.SOURCE.value):
        return (ConnectorTypes.SOURCE, ConnectorRegistrySourceDefinition)
    elif registry_entry.get(ConnectorTypePrimaryKey.DESTINATION.value):
        return (ConnectorTypes.DESTINATION, ConnectorRegistryDestinationDefinition)
    else:
        raise Exception("Could not determine connector type from registry entry")


def _get_directory_write_path(metadata_path: Optional[str], registry_name: str) -> str:
    """Get the write path for the registry entry, assuming the metadata entry is the latest version."""
    if metadata_path is None:
        raise Exception(f"Metadata entry {metadata_entry} does not have a file path")

    metadata_folder = os.path.dirname(metadata_path)
    return os.path.join(metadata_folder, registry_name)


def get_registry_entry_write_path(
    registry_entry: Optional[PolymorphicRegistryEntry], metadata_entry: LatestMetadataEntry, registry_name: str
) -> str:
    """Get the write path for the registry entry."""
    if metadata_entry.is_latest_version_path or metadata_entry.is_release_candidate_version_path:
        # if the metadata entry is the latest or RC version, write the registry entry to the same path as the metadata entry
        return _get_directory_write_path(metadata_entry.file_path, registry_name)
    else:
        if registry_entry is None:
            raise Exception(f"Could not determine write path for registry entry {registry_entry} because it is None")

        # if the metadata entry is not the latest version, write the registry entry to its own version specific path
        # this is handle the case when a dockerImageTag is overridden

        return HACKS.construct_registry_entry_write_path(registry_entry, registry_name)


@sentry_sdk.trace
def persist_registry_entry_to_json(
    registry_entry: PolymorphicRegistryEntry,
    registry_name: str,
    metadata_entry: LatestMetadataEntry,
    registry_directory_manager: GCSFileManager,
) -> GCSFileHandle:
    """Persist the registry_entry to a json file on GCS bucket

    Args:
        registry_entry (ConnectorRegistryV0): The registry_entry.
        registry_name (str): The name of the registry_entry. One of "cloud" or "oss".
        metadata_entry (LatestMetadataEntry): The related Metadata Entry.
        registry_directory_manager (GCSFileHandle): The registry_entry directory manager.

    Returns:
        GCSFileHandle: The registry_entry directory manager.
    """
    registry_entry_write_path = get_registry_entry_write_path(registry_entry, metadata_entry, registry_name)
    registry_entry_json = registry_entry.json(exclude_none=True)
    file_handle = registry_directory_manager.write_data(registry_entry_json.encode("utf-8"), ext="json", key=registry_entry_write_path)
    return file_handle


def generate_registry_entry(
    metadata_entry: LatestMetadataEntry,
    spec_cache: SpecCache,
    registry_name: str,
) -> PolymorphicRegistryEntry:
    """Generate a registry entry given a metadata entry.
    Enriches the metadata entry with spec and release candidate information.

    Args:
        metadata_entry (LatestMetadataEntry): The metadata entry.
        spec_cache (SpecCache): The spec cache.
        registry_name (str): The name of the registry_entry. One of "cloud" or "oss".

    Returns:
        PolymorphicRegistryEntry: The registry entry (could be a source or destination entry).
    """
    raw_entry_dict = metadata_to_registry_entry(metadata_entry, registry_name)
    registry_entry_with_spec = apply_spec_to_registry_entry(raw_entry_dict, spec_cache, registry_name)

    _, ConnectorModel = get_connector_type_from_registry_entry(registry_entry_with_spec)

    return ConnectorModel.parse_obj(registry_entry_with_spec)


@sentry_sdk.trace
def generate_and_persist_registry_entry(
    metadata_entry: LatestMetadataEntry,
    spec_cache: SpecCache,
    metadata_directory_manager: GCSFileManager,
    registry_name: str,
) -> str:
    """Generate the selected registry from the metadata files, and persist it to GCS.

    Args:
        metadata_entry (List[LatestMetadataEntry]): The metadata entry.
        spec_cache (SpecCache): The spec cache.
        metadata_directory_manager (GCSFileManager): The metadata directory manager.
        registry_name (str): The name of the registry_entry. One of "cloud" or "oss".
    Returns:
        str: The public url of the registry entry.
    """
    registry_model = generate_registry_entry(metadata_entry, spec_cache, registry_name)

    file_handle = persist_registry_entry_to_json(registry_model, registry_name, metadata_entry, metadata_directory_manager)

    return file_handle.public_url


def get_registry_status_lists(registry_entry: LatestMetadataEntry) -> Tuple[List[str], List[str]]:
    """Get the enabled registries for the given metadata entry.

    Args:
        registry_entry (LatestMetadataEntry): The metadata entry.

    Returns:
        Tuple[List[str], List[str]]: The enabled and disabled registries.
    """
    metadata_data_dict = registry_entry.metadata_definition.dict()

    # get data.registryOverrides fiield, handling the case where it is not present or none
    registries_field = get(metadata_data_dict, "data.registryOverrides") or {}

    # registries is a dict of registry_name -> {enabled: bool}
    all_enabled_registries = [
        registry_name for registry_name, registry_data in registries_field.items() if registry_data and registry_data.get("enabled")
    ]

    valid_enabled_registries = [registry_name for registry_name in all_enabled_registries if registry_name in VALID_REGISTRIES]

    valid_disabled_registries = [registry_name for registry_name in VALID_REGISTRIES if registry_name not in all_enabled_registries]

    return valid_enabled_registries, valid_disabled_registries


def delete_registry_entry(registry_name, metadata_entry: LatestMetadataEntry, metadata_directory_manager: GCSFileManager) -> str:
    """Delete the given registry entry from GCS.

    Args:
        metadata_entry (LatestMetadataEntry): The registry entry.
        metadata_directory_manager (GCSFileManager): The metadata directory manager.
    """
    registry_entry_write_path = get_registry_entry_write_path(None, metadata_entry, registry_name)
    file_handle = metadata_directory_manager.delete_by_key(key=registry_entry_write_path, ext="json")
    return file_handle.public_url if file_handle else None


@sentry_sdk.trace
def safe_parse_metadata_definition(file_name: str, metadata_dict: dict) -> Optional[MetadataDefinition]:
    """
    Safely parse the metadata definition from the given metadata entry.
    Handles the case where the metadata definition is invalid for in old versions of the metadata.
    """

    try:
        return MetadataDefinition.parse_obj(metadata_dict)

    except ValidationError as e:
        # only raise the error if "latest" is in the path
        if "latest" in file_name:
            raise e
        else:
            print(f"WARNING: Could not parse metadata definition for {file_name}. Error: {e}")
            return None


def safe_get_slack_user_identifier(airbyte_slack_users: pd.DataFrame, metadata_dict: Union[dict, BaseModel]) -> Optional[str]:
    """
    Safely get the slack user identifier from the given git info in the metadata file.
    """
    if isinstance(metadata_dict, BaseModel):
        metadata_dict = to_json_sanitized_dict(metadata_dict)

    # if the slack users is empty or none, return none
    if airbyte_slack_users is None or airbyte_slack_users.empty:
        return None

    commit_author = get(metadata_dict, "data.generated.git.commit_author")
    commit_author_email = get(metadata_dict, "data.generated.git.commit_author_email")

    # if the commit author email is not present, return author name or none
    if not commit_author_email:
        return commit_author

    # if the commit author email is present, try to find the user in the slack users dataframe
    # if the user is not found, return the author name or none
    slack_user = airbyte_slack_users[airbyte_slack_users["email"] == commit_author_email]
    if slack_user.empty:
        slack_user = airbyte_slack_users[airbyte_slack_users["real_name"] == commit_author]

    if slack_user.empty:
        return commit_author

    # if the user is found, return the slack real_name and id e.g. "John Doe (U12345678)"
    slack_id = slack_user["id"].iloc[0]
    slack_real_name = slack_user["real_name"].iloc[0]
    return f"{slack_real_name} (<@{slack_id}>)"


def safe_get_commit_sha(metadata_dict: Union[dict, BaseModel]) -> Optional[str]:
    """
    Safely get the git commit sha from the given git info in the metadata file.
    """
    if isinstance(metadata_dict, BaseModel):
        metadata_dict = to_json_sanitized_dict(metadata_dict)

    # if the git commit sha is not present, return none
    commit_sha = get(metadata_dict, "data.generated.git.commit_sha")
    if not commit_sha:
        return None

    # if the git commit sha is present, return the commit sha
    return commit_sha


# ASSETS


@asset(
    required_resource_keys={"slack", "all_metadata_file_blobs"},
    group_name=GROUP_NAME,
    partitions_def=metadata_partitions_def,
    output_required=False,
    auto_materialize_policy=AutoMaterializePolicy.eager(max_materializations_per_minute=MAX_METADATA_PARTITION_RUN_REQUEST),
)
@sentry.instrument_asset_op
def metadata_entry(context: OpExecutionContext) -> Output[Optional[LatestMetadataEntry]]:
    """Parse and compute the LatestMetadataEntry for the given metadata file."""
    etag = context.partition_key
    context.log.info(f"Processing metadata file with etag {etag}")
    all_metadata_file_blobs = context.resources.all_metadata_file_blobs

    # find the blob with the matching etag
    matching_blob = next((blob for blob in all_metadata_file_blobs if blob.etag == etag), None)
    if not matching_blob:
        raise Exception(f"Could not find blob with etag {etag}")

    airbyte_slack_users = HACKS.get_airbyte_slack_users_from_graph(context)

    metadata_dict = yaml_blob_to_dict(matching_blob)
    user_identifier = safe_get_slack_user_identifier(airbyte_slack_users, metadata_dict)
    commit_sha = safe_get_commit_sha(metadata_dict)

    metadata_file_path = matching_blob.name
    PublishConnectorLifecycle.log(
        context,
        PublishConnectorLifecycleStage.METADATA_VALIDATION,
        StageStatus.IN_PROGRESS,
        f"Found metadata file with path {metadata_file_path} for etag {etag}",
        user_identifier=user_identifier,
        commit_sha=commit_sha,
    )

    # read the matching_blob into a metadata definition
    metadata_def = safe_parse_metadata_definition(matching_blob.name, metadata_dict)

    dagster_metadata = {
        "bucket_name": matching_blob.bucket.name,
        "file_path": metadata_file_path,
        "partition_key": etag,
        "invalid_metadata": metadata_def is None,
    }

    # return only if the metadata definition is valid
    if not metadata_def:
        PublishConnectorLifecycle.log(
            context,
            PublishConnectorLifecycleStage.METADATA_VALIDATION,
            StageStatus.FAILED,
            f"Could not parse metadata definition for {metadata_file_path}, dont panic, this can be expected for old metadata files",
            user_identifier=user_identifier,
            commit_sha=commit_sha,
        )
        return Output(value=None, metadata=dagster_metadata)

    icon_file_path = metadata_file_path.replace(METADATA_FILE_NAME, ICON_FILE_NAME)
    icon_blob = matching_blob.bucket.blob(icon_file_path)

    icon_url = (
        get_public_url_for_gcs_file(icon_blob.bucket.name, icon_blob.name, os.getenv("METADATA_CDN_BASE_URL"))
        if icon_blob.exists()
        else None
    )

    metadata_entry = LatestMetadataEntry(
        metadata_definition=metadata_def,
        icon_url=icon_url,
        bucket_name=matching_blob.bucket.name,
        file_path=metadata_file_path,
        etag=etag,
        last_modified=matching_blob.time_created.isoformat(),
    )

    PublishConnectorLifecycle.log(
        context,
        PublishConnectorLifecycleStage.METADATA_VALIDATION,
        StageStatus.SUCCESS,
        f"Successfully parsed metadata definition for {metadata_file_path}",
        user_identifier=user_identifier,
        commit_sha=commit_sha,
    )

    return Output(value=metadata_entry, metadata=dagster_metadata)


@asset(
    required_resource_keys={"slack", "root_metadata_directory_manager"},
    group_name=GROUP_NAME,
    partitions_def=metadata_partitions_def,
    auto_materialize_policy=AutoMaterializePolicy.eager(max_materializations_per_minute=MAX_METADATA_PARTITION_RUN_REQUEST),
)
@sentry.instrument_asset_op
def registry_entry(
    context: OpExecutionContext,
    metadata_entry: Optional[LatestMetadataEntry],
) -> Output[Optional[dict]]:
    """
    Generate the registry entry files from the given metadata file, and persist it to GCS.
    """
    if not metadata_entry:
        # if the metadata entry is invalid, return an empty dict
        return Output(metadata={"empty_metadata": True}, value=None)

    airbyte_slack_users = HACKS.get_airbyte_slack_users_from_graph(context)

    user_identifier = safe_get_slack_user_identifier(airbyte_slack_users, metadata_entry.metadata_definition)
    commit_sha = safe_get_commit_sha(metadata_entry.metadata_definition)

    PublishConnectorLifecycle.log(
        context,
        PublishConnectorLifecycleStage.REGISTRY_ENTRY_GENERATION,
        StageStatus.IN_PROGRESS,
        f"Generating registry entry for {metadata_entry.file_path}",
        user_identifier=user_identifier,
        commit_sha=commit_sha,
    )

    spec_cache = SpecCache()

    root_metadata_directory_manager = context.resources.root_metadata_directory_manager
    enabled_registries, disabled_registries = get_registry_status_lists(metadata_entry)

    persisted_registry_entries = {
        registry_name: generate_and_persist_registry_entry(
            metadata_entry,
            spec_cache,
            root_metadata_directory_manager,
            registry_name,
        )
        for registry_name in enabled_registries
    }

    # Only delete the registry entry if it is the latest version
    # This is to preserve any registry specific overrides even if they were removed
    deleted_registry_entries = {}
    if metadata_entry.is_latest_version_path:
        context.log.debug(f"Deleting previous registry entries enabled {metadata_entry.file_path}")
        deleted_registry_entries = {
            registry_name: delete_registry_entry(registry_name, metadata_entry, root_metadata_directory_manager)
            for registry_name in disabled_registries
        }

    dagster_metadata_persist = {
        f"create_{registry_name}": MetadataValue.url(registry_url) for registry_name, registry_url in persisted_registry_entries.items()
    }

    dagster_metadata_delete = {
        f"delete_{registry_name}": MetadataValue.url(registry_url) for registry_name, registry_url in deleted_registry_entries.items()
    }

    dagster_metadata = {
        **dagster_metadata_persist,
        **dagster_metadata_delete,
    }

    # Log the registry entries that were created
    for registry_name, registry_url in persisted_registry_entries.items():
        PublishConnectorLifecycle.log(
            context,
            PublishConnectorLifecycleStage.REGISTRY_ENTRY_GENERATION,
            StageStatus.SUCCESS,
            f"Successfully generated {registry_name} registry entry for {metadata_entry.file_path} at {registry_url}.\n\n*This new Connector will be available for use in the platform on the next release (1-3 min)*",
            user_identifier=user_identifier,
            commit_sha=commit_sha,
        )

    # Log the registry entries that were deleted
    for registry_name, registry_url in deleted_registry_entries.items():
        PublishConnectorLifecycle.log(
            context,
            PublishConnectorLifecycleStage.REGISTRY_ENTRY_GENERATION,
            StageStatus.SUCCESS,
            f"Successfully deleted {registry_name} registry entry for {metadata_entry.file_path}",
            user_identifier=user_identifier,
            commit_sha=commit_sha,
        )

    return Output(metadata=dagster_metadata, value=persisted_registry_entries)


def get_registry_entries(blob_resource) -> Output[List]:
    registry_entries = []
    for blob in blob_resource:
        _, registry_entry = read_registry_entry_blob(blob)
        registry_entries.append(registry_entry)

    return Output(registry_entries)


@asset(required_resource_keys={"latest_cloud_registry_entries_file_blobs"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def latest_cloud_registry_entries(context: OpExecutionContext) -> Output[List]:
    return get_registry_entries(context.resources.latest_cloud_registry_entries_file_blobs)


@asset(required_resource_keys={"latest_oss_registry_entries_file_blobs"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def latest_oss_registry_entries(context: OpExecutionContext) -> Output[List]:
    return get_registry_entries(context.resources.latest_oss_registry_entries_file_blobs)


@asset(required_resource_keys={"release_candidate_cloud_registry_entries_file_blobs"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def release_candidate_cloud_registry_entries(context: OpExecutionContext) -> Output[List]:
    return get_registry_entries(context.resources.release_candidate_cloud_registry_entries_file_blobs)


@asset(required_resource_keys={"release_candidate_oss_registry_entries_file_blobs"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def release_candidate_oss_registry_entries(context: OpExecutionContext) -> Output[List]:
    return get_registry_entries(context.resources.release_candidate_oss_registry_entries_file_blobs)
