#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import copy
import json
import logging
from collections import defaultdict
from enum import Enum
from typing import Optional, Union

import sentry_sdk
from google.cloud import storage
from packaging.version import parse as parse_version
from pydash.objects import set_with

from metadata_service.constants import (
    ANALYTICS_BUCKET,
    ANALYTICS_FOLDER,
    METADATA_FOLDER,
    PUBLISH_UPDATE_CHANNEL,
    REGISTRIES_FOLDER,
    VALID_REGISTRIES,
)
from metadata_service.helpers.gcs import get_gcs_storage_client, is_version_yanked, safe_read_gcs_file
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
    try:
        if parse_version(release_candidate_registry_entry.dockerImageTag) < parse_version(
            latest_registry_entry["dockerImageTag"]
        ):
            return latest_registry_entry
    except Exception as e:
        logger.error(f"Error parsing version for release candidate comparison: {e}")
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
def _get_latest_non_yanked_version(
    bucket: storage.Bucket, docker_repository: str, registry_type: str
) -> Optional[PolymorphicRegistryEntry]:
    """Get the latest non-yanked version for a connector.

    This function finds all versions of a connector, sorts them by semver,
    and returns the highest version that is not yanked.

    Args:
        bucket (storage.Bucket): The GCS bucket.
        docker_repository (str): The docker repository (e.g., 'airbyte/source-postgres').
        registry_type (str): The registry type.

    Returns:
        Optional[PolymorphicRegistryEntry]: The latest non-yanked registry entry, or None if all versions are yanked.
    """
    registry_type_file_name = f"{registry_type}.json"

    try:
        logger.info(f"Listing all versions for {docker_repository}")
        prefix = f"{METADATA_FOLDER}/{docker_repository}/"
        blobs = bucket.list_blobs(prefix=prefix)

        versions_with_blobs = []
        for blob in blobs:
            if blob.name.endswith(f"/{registry_type_file_name}"):
                parts = blob.name.split("/")
                if len(parts) >= 5:
                    version = parts[3]
                    if version not in ["latest", "release_candidate"]:
                        versions_with_blobs.append((version, blob))

        if not versions_with_blobs:
            logger.warning(f"No versions found for {docker_repository}")
            return None

        try:
            sorted_versions = sorted(versions_with_blobs, key=lambda x: parse_version(x[0]), reverse=True)
        except Exception as e:
            logger.error(f"Error parsing version for {docker_repository}: {e}")
            sorted_versions = sorted(versions_with_blobs, key=lambda x: x[0], reverse=True)

        for version, blob in sorted_versions:
            if is_version_yanked(bucket, docker_repository, version):
                logger.info(f"Version {version} of {docker_repository} is yanked, skipping")
                continue

            logger.info(f"Using version {version} of {docker_repository} as latest (non-yanked)")
            content = safe_read_gcs_file(blob)
            if not content:
                logger.warning(f"Empty content for {blob.name}, skipping")
                continue

            registry_dict = json.loads(content)
            try:
                if registry_dict.get(ConnectorTypePrimaryKey.SOURCE.value):
                    return ConnectorRegistrySourceDefinition.parse_obj(registry_dict)
                elif registry_dict.get(ConnectorTypePrimaryKey.DESTINATION.value):
                    return ConnectorRegistryDestinationDefinition.parse_obj(registry_dict)
                else:
                    logger.warning(f"Failed to parse registry model for {blob.name}")
                    continue
            except Exception as e:
                logger.error(f"Error parsing registry model for {blob.name}: {e}")
                continue

        logger.warning(f"All versions of {docker_repository} are yanked")
        return None

    except Exception as e:
        logger.error(f"Error finding latest non-yanked version for {docker_repository}: {e}")
        return None


@sentry_sdk.trace
def _get_latest_registry_entries(bucket: storage.Bucket, registry_type: str) -> list[PolymorphicRegistryEntry]:
    """Get the latest registry entries from the GCS bucket.

    This function checks if the current 'latest' version is yanked, and if so,
    falls back to the highest non-yanked version.

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
        content = safe_read_gcs_file(blob)
        if not content:
            logger.warning(f"Empty content for {blob.name}, skipping")
            continue

        registry_dict = json.loads(content)

        parts = blob.name.split("/")
        if len(parts) >= 4:
            docker_repository = f"{parts[1]}/{parts[2]}"
            version = registry_dict.get("dockerImageTag")

            if version and is_version_yanked(bucket, docker_repository, version):
                logger.warning(f"Latest version {version} of {docker_repository} is yanked, finding alternative")
                alternative_entry = _get_latest_non_yanked_version(bucket, docker_repository, registry_type)
                if alternative_entry:
                    latest_registry_entries.append(alternative_entry)
                else:
                    logger.warning(f"No non-yanked version found for {docker_repository}, skipping")
                continue

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

    registry_file_name = f"{registry_name}_registry.json"
    registry_file_path = f"{REGISTRIES_FOLDER}/{registry_file_name}"
    registry_json = registry.json(exclude_none=True)
    registry_json = json.dumps(json.loads(registry_json), sort_keys=True)

    try:
        logger.info(f"Uploading {registry_name} registry to {registry_file_path}")
        blob = bucket.blob(registry_file_path)
        # In cloud, airbyte-cron polls the registry frequently, to enable faster connector updates.
        # We should set a lower cache duration on the blob so that the cron receives an up-to-date view of the registry.
        # However, OSS polls the registry much less frequently, so the default cache setting (1hr max-age) is fine.
        if registry_name == "cloud":
            blob.cache_control = "public, max-age=120"
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
