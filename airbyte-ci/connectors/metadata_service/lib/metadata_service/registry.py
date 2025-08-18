#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import copy
import json
import logging
import os
import urllib.parse
from collections import defaultdict
from enum import Enum
from typing import Optional, Union

import semver
import sentry_sdk
from google.cloud import storage
from google.oauth2 import service_account
from pydash.objects import set_with

from metadata_service.constants import (
    ANALYTICS_BUCKET,
    ANALYTICS_FOLDER,
    METADATA_FOLDER,
    PUBLIC_GCS_BASE_URL,
    PUBLISH_UPDATE_CHANNEL,
    REGISTRIES_FOLDER,
    VALID_REGISTRIES,
)
from metadata_service.helpers.gcs import get_gcs_storage_client, safe_read_gcs_file
from metadata_service.helpers.object_helpers import CaseInsensitiveKeys, default_none_to_dict
from metadata_service.helpers.slack import send_slack_message
from metadata_service.models.generated import ConnectorRegistryDestinationDefinition, ConnectorRegistrySourceDefinition, ConnectorRegistryV0
from metadata_service.models.transform import to_json_sanitized_dict

logger = logging.getLogger(__name__)


PolymorphicRegistryEntry = Union[ConnectorRegistrySourceDefinition, ConnectorRegistryDestinationDefinition]


class ConnectorTypes(str, Enum, metaclass=CaseInsensitiveKeys):
    SOURCE = "source"
    DESTINATION = "destination"


class ConnectorTypePrimaryKey(str, Enum, metaclass=CaseInsensitiveKeys):
    SOURCE = "sourceDefinitionId"
    DESTINATION = "destinationDefinitionId"


class StringNullJsonDecoder(json.JSONDecoder):
    """A JSON decoder that converts "null" strings to None."""

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        return {k: (None if v == "null" else v) for k, v in obj.items()}


def _apply_metrics_to_registry_entry(registry_entry_dict: dict, connector_type: ConnectorTypes, latest_metrics_dict: dict) -> dict:
    """Apply the metrics to the registry entry.

    Args:
        registry_entry_dict (dict): The registry entry.
        latest_metrics_dict (dict): The metrics.

    Returns:
        dict: The registry entry with metrics.
    """
    connector_id = registry_entry_dict[ConnectorTypePrimaryKey[connector_type.value]]
    metrics = latest_metrics_dict.get(connector_id, {})

    # Safely add metrics to ["generated"]["metrics"], knowing that the key may not exist, or might be None
    registry_entry_dict = set_with(registry_entry_dict, "generated.metrics", metrics, default_none_to_dict)

    return registry_entry_dict


def _apply_release_candidate_entries(registry_entry_dict: dict, docker_repository_to_rc_registry_entry: dict) -> dict:
    """Apply the optionally existing release candidate entries to the registry entry.
    We need both the release candidate metadata entry and the release candidate registry entry because the metadata entry contains the rollout configuration, and the registry entry contains the actual RC registry entry.

    Args:
        registry_entry_dict (dict): The registry entry.
        docker_repository_to_rc_registry_entry (dict): Mapping of docker repository to release candidate registry entry.

    Returns:
        dict: The registry entry with release candidates applied.
    """
    registry_entry_dict = copy.deepcopy(registry_entry_dict)
    if registry_entry_dict["dockerRepository"] in docker_repository_to_rc_registry_entry:
        release_candidate_registry_entry = docker_repository_to_rc_registry_entry[registry_entry_dict["dockerRepository"]]
        registry_entry_dict = _apply_release_candidates(registry_entry_dict, release_candidate_registry_entry)
    return registry_entry_dict


def _apply_release_candidates(
    latest_registry_entry: dict,
    release_candidate_registry_entry: PolymorphicRegistryEntry,
) -> dict:
    """Apply the release candidate entries to the registry entry.

    Args:
        latest_registry_entry (dict): The latest registry entry.
        release_candidate_registry_entry (PolymorphicRegistryEntry): The release candidate registry entry.

    Returns:
        dict: The registry entry with release candidates applied.
    """
    try:
        if not release_candidate_registry_entry.releases.rolloutConfiguration.enableProgressiveRollout:
            return latest_registry_entry
    # Handle if releases or rolloutConfiguration is not present in the release candidate registry entry
    except AttributeError:
        return latest_registry_entry

    # If the relase candidate is older than the latest registry entry, don't apply the release candidate and return the latest registry entry
    if semver.Version.parse(release_candidate_registry_entry.dockerImageTag) < semver.Version.parse(
        latest_registry_entry["dockerImageTag"]
    ):
        return latest_registry_entry

    updated_registry_entry = copy.deepcopy(latest_registry_entry)
    updated_registry_entry.setdefault("releases", {})
    updated_registry_entry["releases"]["releaseCandidates"] = {
        release_candidate_registry_entry.dockerImageTag: to_json_sanitized_dict(release_candidate_registry_entry)
    }
    return updated_registry_entry


def _build_connector_registry(
    latest_registry_entries: list[PolymorphicRegistryEntry], latest_connector_metrics: dict, docker_repository_to_rc_registry_entry: dict
) -> ConnectorRegistryV0:
    registry_dict = {"sources": [], "destinations": []}

    for latest_registry_entry in latest_registry_entries:
        connector_type = _get_connector_type_from_registry_entry(latest_registry_entry)
        plural_connector_type = f"{connector_type.value}s"

        registry_entry_dict = to_json_sanitized_dict(latest_registry_entry)

        enriched_registry_entry_dict = _apply_metrics_to_registry_entry(registry_entry_dict, connector_type, latest_connector_metrics)

        enriched_registry_entry_dict = _apply_release_candidate_entries(
            enriched_registry_entry_dict, docker_repository_to_rc_registry_entry
        )

        registry_dict[plural_connector_type].append(enriched_registry_entry_dict)

    return ConnectorRegistryV0.parse_obj(registry_dict)


def _convert_json_to_metrics_dict(jsonl_string: str) -> dict:
    """Convert the jsonl string to a metrics dict.

    Args:
        jsonl_string (str): The jsonl string.

    Returns:
        dict: The metrics dict.
    """
    metrics_dict = defaultdict(dict)
    jsonl_lines = jsonl_string.splitlines()
    for line in jsonl_lines:
        data = json.loads(line, cls=StringNullJsonDecoder)
        connector_data = data["_airbyte_data"]
        connector_definition_id = connector_data["connector_definition_id"]
        airbyte_platform = connector_data["airbyte_platform"]
        metrics_dict[connector_definition_id][airbyte_platform] = connector_data

    return metrics_dict


def _get_connector_type_from_registry_entry(registry_entry: PolymorphicRegistryEntry) -> ConnectorTypes:
    """Get the connector type from the registry entry.

    Args:
        registry_entry (PolymorphicRegistryEntry): The registry entry.

    Returns:
        ConnectorTypes: The connector type.
    """
    if hasattr(registry_entry, ConnectorTypePrimaryKey.SOURCE):
        return ConnectorTypes.SOURCE
    elif hasattr(registry_entry, ConnectorTypePrimaryKey.DESTINATION):
        return ConnectorTypes.DESTINATION
    else:
        raise ValueError("Registry entry is not a source or destination")


@sentry_sdk.trace
def _get_latest_registry_entries(bucket: storage.Bucket, registry_type: str) -> list[PolymorphicRegistryEntry]:
    """Get the latest registry entries from the GCS bucket.

    Args:
        bucket (storage.Bucket): The GCS bucket.
        registry_type (str): The registry type.

    Returns:
        list[PolymorphicRegistryEntry]: The latest registry entries.
    """
    registry_type_file_name = f"{registry_type}.json"

    try:
        logger.info(f"Listing blobs in the latest folder: {METADATA_FOLDER}/**/latest/{registry_type_file_name}")
        blobs = bucket.list_blobs(match_glob=f"{METADATA_FOLDER}/**/latest/{registry_type_file_name}")
    except Exception as e:
        logger.error(f"Error listing blobs in the latest folder: {str(e)}")
        return []

    latest_registry_entries = []
    for blob in blobs:
        logger.info(f"Reading blob: {blob.name}")
        registry_dict = json.loads(safe_read_gcs_file(blob))
        try:
            if registry_dict.get(ConnectorTypePrimaryKey.SOURCE.value):
                registry_model = ConnectorRegistrySourceDefinition.parse_obj(registry_dict)
            elif registry_dict.get(ConnectorTypePrimaryKey.DESTINATION.value):
                registry_model = ConnectorRegistryDestinationDefinition.parse_obj(registry_dict)
            else:
                logger.warning(f"Failed to parse registry model for {blob.name}. Skipping.")
                continue
        except Exception as e:
            logger.error(f"Error parsing registry model for {blob.name}: {str(e)}")
            continue
        latest_registry_entries.append(registry_model)
    return latest_registry_entries


@sentry_sdk.trace
def _get_release_candidate_registry_entries(bucket: storage.Bucket, registry_type: str) -> list[PolymorphicRegistryEntry]:
    """Get the release candidate registry entries from the GCS bucket.

    Args:
        bucket (storage.Bucket): The GCS bucket.
        registry_type (str): The registry type.

    Returns:
        list[PolymorphicRegistryEntry]: The release candidate registry entries.
    """
    blobs = bucket.list_blobs(match_glob=f"{METADATA_FOLDER}/**/release_candidate/{registry_type}.json")
    release_candidate_registry_entries = []
    for blob in blobs:
        logger.info(f"Reading blob: {blob.name}")
        registry_dict = json.loads(safe_read_gcs_file(blob))
        try:
            if "/source-" in blob.name:
                registry_model = ConnectorRegistrySourceDefinition.parse_obj(registry_dict)
            else:
                registry_model = ConnectorRegistryDestinationDefinition.parse_obj(registry_dict)
        except Exception as e:
            logger.error(f"Error parsing registry model for {blob.name}: {str(e)}")
            continue

        release_candidate_registry_entries.append(registry_model)
    return release_candidate_registry_entries


@sentry_sdk.trace
def _get_latest_connector_metrics(bucket: storage.Bucket) -> dict:
    """Get the latest connector metrics from the GCS bucket.

    Args:
        bucket (storage.Bucket): The GCS bucket.

    Returns:
        dict: The latest connector metrics.
    """
    try:
        logger.info(f"Getting blobs in the analytics folder: {ANALYTICS_FOLDER}")
        blobs = bucket.list_blobs(prefix=f"{ANALYTICS_FOLDER}/")
    except Exception as e:
        logger.error(f"Unexpected error listing blobs at {ANALYTICS_FOLDER}: {str(e)}")
        return {}

    if not blobs:
        raise ValueError("No blobs found in the analytics folder")

    # Sort blobs by updated time (most recent first)
    most_recent_blob = max(blobs, key=lambda blob: blob.updated)

    latest_metrics_jsonl = safe_read_gcs_file(most_recent_blob)

    if latest_metrics_jsonl is None:
        logger.warning(f"No metrics found for {most_recent_blob.name}")
        return {}

    try:
        latest_metrics_dict = _convert_json_to_metrics_dict(latest_metrics_jsonl)
    except Exception as e:
        logger.error(f"Error converting json to metrics dict: {str(e)}")
        return {}

    return latest_metrics_dict


@sentry_sdk.trace
def _persist_registry(registry: ConnectorRegistryV0, registry_name: str, bucket: storage.Bucket) -> None:
    """Persist the registry to a json file on GCS bucket

    Args:
        registry (ConnectorRegistryV0): The registry.
        registry_name (str): The name of the registry. One of "cloud" or "oss".
        bucket (storage.Bucket): The GCS bucket.

    Returns:
        None
    """

    # TODO: Remove the dev bucket set up once registry artificts have been validated and then add the bucket as a parameter. This block exists so we can write the registry artifacts to the dev bucket for validation.
    gcs_creds = os.environ.get("GCS_DEV_CREDENTIALS")
    service_account_info = json.loads(gcs_creds)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    client = storage.Client(credentials=credentials)
    bucket = client.bucket("dev-airbyte-cloud-connector-metadata-service")

    registry_file_name = f"{registry_name}_registry.json"
    registry_file_path = f"{REGISTRIES_FOLDER}/{registry_file_name}"
    registry_json = registry.json(exclude_none=True)
    registry_json = json.dumps(json.loads(registry_json), sort_keys=True)

    try:
        logger.info(f"Uploading {registry_name} registry to {registry_file_path}")
        blob = bucket.blob(registry_file_path)
        blob.upload_from_string(registry_json.encode("utf-8"), content_type="application/json")
        logger.info(f"Successfully uploaded {registry_name} registry to {registry_file_path}")
        return
    except Exception as e:
        logger.error(f"Error persisting {registry_file_name} to json: {str(e)}")
        raise e


def generate_and_persist_connector_registry(bucket_name: str, registry_type: str) -> None:
    """Generate and persist the registry to a json file on GCS bucket.

    Args:
        bucket_name (str): The name of the GCS bucket.
        registry_type (str): The type of the registry.

    Returns:
        tuple[bool, Optional[str]]: A tuple containing a boolean indicating success and an optional error message.
    """
    if registry_type not in VALID_REGISTRIES:
        raise ValueError(f"Invalid registry type: {registry_type}. Valid types are: {', '.join(VALID_REGISTRIES)}.")

    gcs_client = get_gcs_storage_client()
    registry_bucket = gcs_client.bucket(bucket_name)
    analytics_bucket = gcs_client.bucket(ANALYTICS_BUCKET)

    latest_registry_entries = _get_latest_registry_entries(registry_bucket, registry_type)

    release_candidate_registry_entries = _get_release_candidate_registry_entries(registry_bucket, registry_type)

    docker_repository_to_rc_registry_entry = {
        release_candidate_registry_entries.dockerRepository: release_candidate_registry_entries
        for release_candidate_registry_entries in release_candidate_registry_entries
    }

    latest_connector_metrics = _get_latest_connector_metrics(analytics_bucket)

    connector_registry = _build_connector_registry(
        latest_registry_entries, latest_connector_metrics, docker_repository_to_rc_registry_entry
    )

    try:
        _persist_registry(connector_registry, registry_type, registry_bucket)
    except Exception as e:
        message = f"*🤖 🔴 _Registry Generation_ FAILED*:\nFailed to generate and persist {registry_type} registry."
        send_slack_message(PUBLISH_UPDATE_CHANNEL, message)
        raise e
