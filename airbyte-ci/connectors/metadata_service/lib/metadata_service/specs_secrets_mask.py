#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
import json
import logging
import os
from typing import Set

import dpath.util
import sentry_sdk
import yaml
from google.cloud import storage
from google.oauth2 import service_account

from metadata_service.constants import PUBLISH_UPDATE_CHANNEL, REGISTRIES_FOLDER, SPECS_SECRETS_MASK_FILE_NAME, VALID_REGISTRIES
from metadata_service.helpers.gcs import get_gcs_storage_client, safe_read_gcs_file
from metadata_service.helpers.slack import send_slack_message
from metadata_service.models.generated import ConnectorRegistryV0
from metadata_service.models.transform import to_json_sanitized_dict
from metadata_service.registry import PolymorphicRegistryEntry

logger = logging.getLogger(__name__)


@sentry_sdk.trace
def _get_registries_from_gcs(bucket: storage.Bucket) -> list[ConnectorRegistryV0]:
    """Get the registries from GCS and return a list of ConnectorRegistryV0 objects."""
    registries = []
    for registry in VALID_REGISTRIES:
        registry_name = f"{registry}_registry.json"
        try:
            logger.info(f"Getting registry {registry_name} from GCS")
            blob = bucket.blob(f"{REGISTRIES_FOLDER}/{registry_name}")
            registry_dict = json.loads(safe_read_gcs_file(blob))
            registries.append(ConnectorRegistryV0.parse_obj(registry_dict))
        except Exception as e:
            logger.error(f"Error getting registry {registry_name} from GCS: {e}")
            raise e

    return registries


def _get_specs_secrets_from_registry_entries(entries: list[PolymorphicRegistryEntry]) -> Set[str]:
    """Get the specs secrets from the registry entries and return a set of secret properties."""
    secret_properties = set()
    for entry in entries:
        sanitized_entry = to_json_sanitized_dict(entry)
        spec_properties = sanitized_entry["spec"]["connectionSpecification"].get("properties")
        if spec_properties is None:
            continue
        for type_path, _ in dpath.util.search(spec_properties, "**/type", yielded=True):
            absolute_path = f"/{type_path}"
            if "/" in type_path:
                property_path, _ = absolute_path.rsplit(sep="/", maxsplit=1)
            else:
                property_path = absolute_path
            property_definition = dpath.util.get(spec_properties, property_path)
            marked_as_secret = property_definition.get("airbyte_secret", False)
            if marked_as_secret:
                secret_properties.add(property_path.split("/")[-1])

    return secret_properties


@sentry_sdk.trace
def _persist_secrets_to_gcs(specs_secrets: Set[str], bucket: storage.Bucket) -> None:
    """Persist the specs secrets to GCS."""
    specs_secrets_mask_blob = bucket.blob(f"{REGISTRIES_FOLDER}/{SPECS_SECRETS_MASK_FILE_NAME}")

    try:
        logger.info(f"Uploading specs secrets mask to GCS: {specs_secrets_mask_blob.name}")
        specs_secrets_mask_blob.upload_from_string(yaml.dump({"properties": sorted(list(specs_secrets))}))
    except Exception as e:
        logger.error(f"Error uploading specs secrets mask to GCS: {e}")
        raise e


def generate_and_persist_specs_secrets_mask(bucket_name: str) -> None:
    """Generate and persist the specs secrets mask to GCS.

    Args:
        bucket_name (str): The name of the bucket to persist the specs secrets mask to.

    Returns:
        None
    """

    client = get_gcs_storage_client()
    bucket = client.bucket(bucket_name)

    registries = _get_registries_from_gcs(bucket)
    all_entries = [entry for registry in registries for entry in registry.sources + registry.destinations]

    all_specs_secrets = _get_specs_secrets_from_registry_entries(all_entries)

    try:
        _persist_secrets_to_gcs(all_specs_secrets, bucket)
    except Exception as e:
        message = f"*🤖 🔴 _Specs Secrets Mask Generation_ FAILED*:\nFailed to generate and persist `{SPECS_SECRETS_MASK_FILE_NAME}` to registry GCS bucket."
        send_slack_message(PUBLISH_UPDATE_CHANNEL, message)
