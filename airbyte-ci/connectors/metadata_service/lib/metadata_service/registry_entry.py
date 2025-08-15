#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import datetime
import json
import logging
import os
import pathlib
from typing import List, Optional, Tuple, Union

import pandas as pd
import sentry_sdk
import yaml
from google.cloud import storage
from pydash import set_with

from metadata_service.constants import (
    CONNECTOR_DEPENDENCY_FILE_NAME,
    CONNECTOR_DEPENDENCY_FOLDER,
    DEFAULT_ASSET_URL,
    ICON_FILE_NAME,
    METADATA_CDN_BASE_URL,
    METADATA_FILE_NAME,
    METADATA_FOLDER,
    PUBLISH_UPDATE_CHANNEL,
)
from metadata_service.helpers.gcs import get_gcs_storage_client, safe_read_gcs_file
from metadata_service.helpers.object_helpers import deep_copy_params, default_none_to_dict
from metadata_service.helpers.slack import send_slack_message
from metadata_service.models.generated import ConnectorRegistryDestinationDefinition, ConnectorRegistrySourceDefinition
from metadata_service.registry import ConnectorTypePrimaryKey, ConnectorTypes

logger = logging.getLogger(__name__)

DEV_BUCKET = "dev-airbyte-cloud-connector-metadata-service"


PolymorphicRegistryEntry = Union[ConnectorRegistrySourceDefinition, ConnectorRegistryDestinationDefinition]
TaggedRegistryEntry = Tuple[ConnectorTypes, PolymorphicRegistryEntry]


def _apply_metadata_overrides(metadata_data: dict, registry_type: str, bucket_name: str) -> dict:
    connector_type = metadata_data["connectorType"]

    overridden_metadata_data = _apply_overrides_from_registry(metadata_data, registry_type)

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
    overridden_metadata_data["generated"] = _apply_generated_fields(overridden_metadata_data, bucket_name)

    # Add Dependency information
    overridden_metadata_data["packageInfo"] = _apply_package_info_fields(overridden_metadata_data, bucket_name)

    # Add language field
    overridden_metadata_data = _apply_language_field(overridden_metadata_data)

    # if there is no supportLevel, set it to "community"
    if not overridden_metadata_data.get("supportLevel"):
        overridden_metadata_data["supportLevel"] = "community"

    # apply ab_internal defaults
    overridden_metadata_data = _apply_ab_internal_defaults(overridden_metadata_data)

    # apply icon url and releases
    icon_blob = _get_icon_blob_from_gcs(bucket_name, metadata_data)
    icon_url = _get_public_url_for_gcs_file(icon_blob.bucket.name, icon_blob.name, METADATA_CDN_BASE_URL)

    overridden_metadata_data["iconUrl"] = icon_url
    overridden_metadata_data["releases"] = _apply_connector_releases(overridden_metadata_data)

    return overridden_metadata_data


@deep_copy_params
def _apply_overrides_from_registry(metadata_data: dict, override_registry_key: str) -> dict:
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
def _apply_generated_fields(metadata_data: dict, bucket_name: str) -> dict:
    """Apply generated fields to the metadata data field.

    Args:
        metadata_data (dict): The metadata data field.

    Returns:
        dict: The metadata data field with the generated fields applied.
    """
    generated_fields = metadata_data.get("generated") or {}

    metadata_file_path = f"{METADATA_FOLDER}/{metadata_data['dockerRepository']}/{metadata_data['dockerImageTag']}/{METADATA_FILE_NAME}"

    # Add the source file metadata
    generated_fields = set_with(generated_fields, "source_file_info.metadata_file_path", metadata_file_path, default_none_to_dict)
    generated_fields = set_with(generated_fields, "source_file_info.metadata_bucket_name", bucket_name, default_none_to_dict)
    generated_fields = set_with(
        generated_fields, "source_file_info.registry_entry_generated_at", datetime.datetime.now().isoformat(), default_none_to_dict
    )

    return generated_fields


@sentry_sdk.trace
@deep_copy_params
def _apply_package_info_fields(metadata_data: dict, bucket_name: str) -> dict:
    """Apply package info fields to the metadata data field.

    Args:
        metadata_data (dict): The metadata data field.
        bucket_name (str): The name of the GCS bucket.

    Returns:
        dict: The metadata data field with the package info fields applied.
    """

    sanitized_connector_technical_name = metadata_data["dockerRepository"].replace("airbyte/", "")
    connector_version = metadata_data["dockerImageTag"]

    dependencies_path = (
        f"{CONNECTOR_DEPENDENCY_FOLDER}/{sanitized_connector_technical_name}/{connector_version}/{CONNECTOR_DEPENDENCY_FILE_NAME}"
    )

    try:
        logger.info(
            f"Getting dependencies blob for `{sanitized_connector_technical_name}` `{connector_version}` at path `{dependencies_path}`"
        )
        gcs_client = get_gcs_storage_client(gcs_creds=os.environ.get("GCS_CREDENTIALS"))
        bucket = gcs_client.bucket(bucket_name)
        dependencies_blob = bucket.blob(dependencies_path)
        dependencies_json = json.loads(safe_read_gcs_file(dependencies_blob))
    except Exception as e:
        logger.warning(f"Error reading dependencies file for `{sanitized_connector_technical_name}`: {e}")
        raise

    cdk_version = None
    for package in dependencies_json.get("dependencies", []):
        if package.get("package_name") == "airbyte-cdk":
            cdk_version = package.get("version")
            break

    package_info_fields = metadata_data.get("packageInfo") or {}
    package_info_fields = set_with(package_info_fields, "cdk_version", cdk_version, default_none_to_dict)

    logger.info("Added package info fields.")

    return package_info_fields


@deep_copy_params
def _apply_language_field(metadata_data: dict) -> dict:
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
def _apply_ab_internal_defaults(metadata_data: dict) -> dict:
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
def _apply_connector_releases(metadata: dict) -> Optional[pd.DataFrame]:
    documentation_url = metadata["documentationUrl"]
    final_registry_releases = {}
    releases = metadata.get("releases")
    if releases is not None and releases.get("breakingChanges"):
        # apply defaults for connector releases
        final_registry_releases["migrationDocumentationUrl"] = _calculate_migration_documentation_url(
            metadata["releases"], documentation_url
        )

        # releases has a dictionary field called breakingChanges, where the key is the version and the value is the data for the breaking change
        # each breaking change has a migrationDocumentationUrl field that is optional, so we need to apply defaults to it
        breaking_changes = metadata["releases"]["breakingChanges"]
        if breaking_changes is not None:
            for version, breaking_change in breaking_changes.items():
                breaking_change["migrationDocumentationUrl"] = _calculate_migration_documentation_url(
                    breaking_change, documentation_url, version
                )
            final_registry_releases["breakingChanges"] = breaking_changes

    if releases is not None and releases.get("rolloutConfiguration"):
        final_registry_releases["rolloutConfiguration"] = metadata["releases"]["rolloutConfiguration"]
    return final_registry_releases


def _calculate_migration_documentation_url(releases_or_breaking_change: dict, documentation_url: str, version: Optional[str] = None) -> str:
    """Calculate the migration documentation url for the connector releases.

    Args:
        metadata_releases (dict): The connector releases.

    Returns:
        str: The migration documentation url.
    """

    base_url = f"{documentation_url}-migrations"
    default_migration_documentation_url = f"{base_url}#{version}" if version is not None else base_url

    return releases_or_breaking_change.get("migrationDocumentationUrl", None) or default_migration_documentation_url


def _get_and_parse_yaml_file(file_path: pathlib.Path) -> dict:
    """Get and parse the metadata file.

    Args:
        metadata_file_path (pathlib.Path): The path to the metadata file.

    Returns:
        dict: The file dictionary.
    """

    try:
        logger.debug(f"Getting and parsing YAML file: `{file_path}`")
        with open(file_path, "r") as f:
            file_dict = yaml.safe_load(f)
    except Exception as e:
        logger.exception(f"Error parsing file")
        raise
    logger.info("Parsed YAML file.")
    return file_dict


def _get_and_parse_json_file(file_path: pathlib.Path) -> dict:
    """Get and parse the json file.

    Args:
        file_path (pathlib.Path): The path to the file.

    Returns:
        dict: The file dictionary.
    """
    try:
        logger.debug(f"Getting and parsing JSON file: `{file_path}`")
        with open(file_path, "r") as f:
            file_dict = json.load(f)
    except Exception as e:
        logger.exception(f"Error parsing JSON file: `{file_path}`")
        raise
    logger.info("Parsed JSON file.")
    return file_dict


@sentry_sdk.trace
def _get_icon_blob_from_gcs(bucket_name: str, metadata_entry: dict) -> storage.Blob:
    """Get the icon blob from the GCS bucket.

    Args:
        bucket (storage.Bucket): The GCS bucket.
        metadata_entry (dict): The metadata entry.

    Returns:
        storage.Blob: The icon blob.
    """
    connector_docker_repository = metadata_entry["dockerRepository"]
    icon_file_path = f"{METADATA_FOLDER}/{connector_docker_repository}/latest/{ICON_FILE_NAME}"
    try:
        logger.info(f"Getting icon blob for {connector_docker_repository}")
        gcs_client = get_gcs_storage_client(gcs_creds=os.environ.get("GCS_CREDENTIALS"))
        bucket = gcs_client.bucket(bucket_name)
        icon_blob = bucket.blob(icon_file_path)
        if not icon_blob.exists():
            raise ValueError(f"Icon file not found for `{connector_docker_repository}`")
    except Exception as e:
        logger.exception(f"Error getting icon blob")
        raise
    return icon_blob


def _get_public_url_for_gcs_file(bucket_name: str, file_path: str, cdn_url: Optional[str] = None) -> str:
    """Get the public URL to a file in the GCS bucket.

    Args:
        bucket_name: The name of the GCS bucket.
        file_path: The path to the file in the bucket.
        cdn_url: The base URL of the CDN that serves the bucket.

    Returns:
        The public URL to the file.
    """
    return f"{cdn_url}/{file_path}" if cdn_url else f"{DEFAULT_ASSET_URL}/{bucket_name}/{file_path}"


def _get_connector_type_from_registry_entry(registry_entry: dict) -> TaggedRegistryEntry:
    """Get the connector type from the registry entry.

    Args:
        registry_entry (dict): The registry entry.

    Returns:
        TaggedRegistryEntry: The connector type and model.
    """
    if registry_entry.get(ConnectorTypePrimaryKey.SOURCE.value):
        return (ConnectorTypes.SOURCE, ConnectorRegistrySourceDefinition)
    elif registry_entry.get(ConnectorTypePrimaryKey.DESTINATION.value):
        return (ConnectorTypes.DESTINATION, ConnectorRegistryDestinationDefinition)
    else:
        raise Exception("Could not determine connector type from registry entry")


def _get_registry_entry_blob_paths(metadata_dict: dict, registry_type: str) -> List[str]:
    """
    Builds the registry entry paths for the registry entries.

    Args:
        metadata_dict (dict): The metadata dictionary.
        registry_type (str): The registry type.

    Returns:
        List[str]: The registry entry paths.
    """
    registry_entry_paths = []
    if "-rc" not in metadata_dict["data"]["dockerImageTag"] and "-dev" not in metadata_dict["data"]["dockerImageTag"]:
        latest_registry_entry_path = f"{METADATA_FOLDER}/{metadata_dict['data']['dockerRepository']}/latest/{registry_type}.json"
        versioned_registry_entry_path = (
            f"{METADATA_FOLDER}/{metadata_dict['data']['dockerRepository']}/{metadata_dict['data']['dockerImageTag']}/{registry_type}.json"
        )

        registry_entry_paths.append(latest_registry_entry_path)
        registry_entry_paths.append(versioned_registry_entry_path)

    elif "-rc" in metadata_dict["data"]["dockerImageTag"]:
        release_candidate_registry_entry_path = (
            f"{METADATA_FOLDER}/{metadata_dict['data']['dockerRepository']}/release_candidate/{registry_type}.json"
        )
        versioned_registry_entry_path = (
            f"{METADATA_FOLDER}/{metadata_dict['data']['dockerRepository']}/{metadata_dict['data']['dockerImageTag']}/{registry_type}.json"
        )
        registry_entry_paths.append(release_candidate_registry_entry_path)

    elif "-dev" in metadata_dict["data"]["dockerImageTag"]:
        dev_registry_entry_path = (
            f"{METADATA_FOLDER}/{metadata_dict['data']['dockerRepository']}/{metadata_dict['data']['dockerImageTag']}/{registry_type}.json"
        )
        registry_entry_paths.append(dev_registry_entry_path)

    return registry_entry_paths


@sentry_sdk.trace
def _persist_connector_registry_entry(bucket_name: str, registry_entry: PolymorphicRegistryEntry, registry_entry_path: str) -> None:
    """Persist the connector registry entry to the GCS bucket.

    Args:
        bucket_name (str): The name of the GCS bucket.
        registry_entry (PolymorphicRegistryEntry): The registry entry.
        registry_entry_path (str): The path to the registry entry.
    """
    try:
        logger.info(f"Persisting connector registry entry to {registry_entry_path}")
        gcs_client = get_gcs_storage_client(gcs_creds=os.environ.get("GCS_DEV_CREDENTIALS"))
        bucket = gcs_client.bucket(DEV_BUCKET)
        registry_entry_blob = bucket.blob(registry_entry_path)
        registry_entry_blob.upload_from_string(registry_entry.json(exclude_none=True))
    except Exception as e:
        logger.exception(f"Error persisting connector registry entry")
        raise


@sentry_sdk.trace
def generate_and_persist_registry_entry(
    bucket_name: str, metadata_file_path: pathlib.Path, spec_path: pathlib.Path, registry_type: str
) -> None:
    """Generate and persist the connector registry entry to the GCS bucket.

    Args:
        bucket_name (str): The name of the GCS bucket.
        metadata_file_path (pathlib.Path): The path to the metadata file.
        spec_path (pathlib.Path): The path to the spec file.
        registry_type (str): The registry type.
    """

    # It can be assumed the metadata file has already been validated before getting to this stage.
    metadata_dict = _get_and_parse_yaml_file(metadata_file_path)

    message = f"*🤖 🟡 _Registry Entry Generation_ STARTED*:\nRegistry Entry: `{registry_type}.json`\nConnector: `{metadata_dict['data']['dockerRepository']}`\nGCS Bucket: `{bucket_name}`."
    send_slack_message(PUBLISH_UPDATE_CHANNEL, message)

    # If the connector is not enabled on the given registry, skip generateing and persisting the registry entry.
    if metadata_dict["data"]["registryOverrides"][registry_type]["enabled"]:
        registry_entry_blob_paths = _get_registry_entry_blob_paths(metadata_dict, registry_type)

        metadata_data = metadata_dict["data"]

        try:
            overridden_metadata_data = _apply_metadata_overrides(metadata_data, registry_type, bucket_name)
        except Exception as e:
            logger.exception(f"Error applying metadata overrides")
            message = f"*🤖 🔴 _Registry Entry Generation_ FAILED*:\nRegistry Entry: `{registry_type}.json`\nConnector: `{metadata_data['dockerRepository']}`\nGCS Bucket: `{bucket_name}`."
            send_slack_message(PUBLISH_UPDATE_CHANNEL, message)
            raise

        logger.info("Parsing spec file.")
        overridden_metadata_data["spec"] = _get_and_parse_json_file(spec_path)
        logger.info("Spec file parsed and added to metadata.")

        logger.info("Parsing registry entry model.")
        _, RegistryEntryModel = _get_connector_type_from_registry_entry(overridden_metadata_data)
        registry_entry_model = RegistryEntryModel.parse_obj(overridden_metadata_data)
        logger.info("Registry entry model parsed.")

        # Persist the registry entry to the GCS bucket.
        for registry_entry_blob_path in registry_entry_blob_paths:
            try:
                logger.info(
                    f"Persisting `{metadata_data['dockerRepository']}` {registry_type} registry entry to `{registry_entry_blob_path}`"
                )

                _persist_connector_registry_entry(bucket_name, registry_entry_model, registry_entry_blob_path)

                message = f"*🤖 🟢 _Registry Entry Generation_ SUCCESS*:\nRegistry Entry: `{registry_type}.json`\nConnector: `{metadata_data['dockerRepository']}`\nGCS Bucket: `{bucket_name}`\nPath: `{registry_entry_blob_path}`."
                send_slack_message(PUBLISH_UPDATE_CHANNEL, message)

                logger.info("Success.")

            except Exception as e:
                logger.exception(f"Error persisting connector registry entry to")

                message = f"*🤖 🔴 _Registry Entry Generation_ FAILED*:\nRegistry Entry: `{registry_type}.json`\nConnector: `{metadata_data['dockerRepository']}`\nGCS Bucket: `{bucket_name}`\nPath: `{registry_entry_blob_path}`."
                send_slack_message(PUBLISH_UPDATE_CHANNEL, message)

                try:
                    bucket = get_gcs_storage_client(gcs_creds=os.environ.get("GCS_DEV_CREDENTIALS")).bucket(DEV_BUCKET)
                    bucket.delete_blob(registry_entry_blob_path)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up {registry_entry_blob_path}: {cleanup_error}")
                raise
    else:
        logger.info(
            f"Registry type {registry_type} is not enabled for `{metadata_dict['data']['dockerRepository']}`, skipping generation and upload."
        )
        message = f"*🤖 ⚫ _Registry Entry Generation_ NOOP*:\n_Note: Connector is not enabled on {registry_type} registry. No action required._\nRegistry Entry: `{registry_type}.json`\nConnector: `{metadata_dict['data']['dockerRepository']}`\nGCS Bucket: `{bucket_name}`."
        send_slack_message(PUBLISH_UPDATE_CHANNEL, message)

    # For latest versions that are disabled, delete any existing registry entry to remove it from the registry
    if (
        "-rc" not in metadata_dict["data"]["dockerImageTag"] and "-dev" not in metadata_dict["data"]["dockerImageTag"]
    ) and not metadata_dict["data"]["registryOverrides"][registry_type]["enabled"]:
        logger.info(
            f"{registry_type} is not enabled: deleting existing {registry_type} registry entry for {metadata_dict['data']['dockerRepository']} at latest path."
        )

        latest_registry_entry_path = f"{METADATA_FOLDER}/{metadata_dict['data']['dockerRepository']}/latest/{registry_type}.json"

        bucket = get_gcs_storage_client(gcs_creds=os.environ.get("GCS_DEV_CREDENTIALS")).bucket(DEV_BUCKET)
        existing_registry_entry = bucket.blob(latest_registry_entry_path)
        if existing_registry_entry.exists():
            bucket.delete_blob(latest_registry_entry_path)
