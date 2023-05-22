#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pathlib import Path
from typing import Tuple

import yaml
import base64
import hashlib
import json
import os

from google.cloud import storage
from google.oauth2 import service_account

from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.constants import METADATA_FILE_NAME, METADATA_FOLDER
from metadata_service.validators.metadata_validator import validate_metadata_images_in_dockerhub


def get_metadata_file_path(dockerRepository: str, version: str) -> str:
    """Get the path to the metadata file for a specific version of a connector.

    Args:
        dockerRepository (str): Name of the connector docker image.
        version (str): Version of the connector.
    Returns:
        str: Path to the metadata file.
    """
    return f"{METADATA_FOLDER}/{dockerRepository}/{version}/{METADATA_FILE_NAME}"


def compute_gcs_md5(file_name: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return base64.b64encode(hash_md5.digest()).decode("utf8")


def _save_blob_to_gcs(blob_to_save: storage.blob.Blob, file_path: str) -> bool:
    """Uploads a file to the bucket."""
    print(f"Uploading {file_path} to {blob_to_save.name}...")

    # Set Cache-Control header to no-cache to avoid caching issues
    # This is IMPORTANT because if we don't set this header, the metadata file will be cached by GCS
    # and the next time we try to download it, we will get the stale version
    blob_to_save.cache_control = "no-cache"

    blob_to_save.upload_from_filename(file_path)

    return True


def upload_metadata_to_gcs(bucket_name: str, metadata_file_path: Path) -> Tuple[bool, str]:
    """Upload a metadata file to a GCS bucket.

    If the per 'version' key already exists it won't be overwritten.
    Also updates the 'latest' key on each new version.

    Args:
        bucket_name (str): Name of the GCS bucket to which the metadata file will be uploade.
        metadata_file_path (Path): Path to the metadata file.
        service_account_file_path (Path): Path to the JSON file with the service account allowed to read and write on the bucket.
    Returns:
        Tuple[bool, str]: Whether the metadata file was uploaded and its blob id.
    """
    uploaded = False
    raw_metadata = yaml.safe_load(metadata_file_path.read_text())
    metadata = ConnectorMetadataDefinitionV0.parse_obj(raw_metadata)

    service_account_info = json.loads(os.environ.get("GCS_CREDENTIALS"))
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)

    version_path = get_metadata_file_path(metadata.data.dockerRepository, metadata.data.dockerImageTag)
    latest_path = get_metadata_file_path(metadata.data.dockerRepository, "latest")

    version_blob = bucket.blob(version_path)
    latest_blob = bucket.blob(latest_path)

    # reload the blobs to get the md5_hash
    if version_blob.exists():
        version_blob.reload()
    if latest_blob.exists():
        latest_blob.reload()

    metadata_file_md5_hash = compute_gcs_md5(metadata_file_path)
    version_blob_md5_hash = version_blob.md5_hash if version_blob.exists() else None
    latest_blob_md5_hash = latest_blob.md5_hash if latest_blob.exists() else None

    print(f"Local Metadata md5_hash: {metadata_file_md5_hash}")
    print(f"Current Version blob md5_hash: {version_blob_md5_hash}")
    print(f"Latest blob md5_hash: {latest_blob_md5_hash}")

    trigger_version_upload = metadata_file_md5_hash != version_blob_md5_hash
    trigger_latest_upload = metadata_file_md5_hash != latest_blob_md5_hash

    # Validate that the images are on DockerHub
    if trigger_version_upload or trigger_latest_upload:
        print("Validating that the images are on DockerHub...")
        is_valid, error = validate_metadata_images_in_dockerhub(metadata)
        if not is_valid:
            raise ValueError(error)

    # upload if md5_hash is different
    if trigger_version_upload:
        uploaded = _save_blob_to_gcs(version_blob, str(metadata_file_path))

    if trigger_latest_upload:
        uploaded = _save_blob_to_gcs(latest_blob, str(metadata_file_path))

    return uploaded, version_blob.id
