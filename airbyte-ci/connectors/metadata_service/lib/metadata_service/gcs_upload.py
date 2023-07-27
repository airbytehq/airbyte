#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pathlib import Path
from typing import Tuple, Optional
from pydash.objects import get

import base64
import hashlib
import json
import os
import yaml

from google.cloud import storage
from google.oauth2 import service_account

from metadata_service.constants import METADATA_FILE_NAME, METADATA_FOLDER, ICON_FILE_NAME
from metadata_service.validators.metadata_validator import POST_UPLOAD_VALIDATORS, validate_and_load
from metadata_service.utils import to_json_sanitized_dict
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0

from dataclasses import dataclass


@dataclass(frozen=True)
class MetadataUploadInfo:
    uploaded: bool
    latest_uploaded: bool
    latest_blob_id: Optional[str]
    version_uploaded: bool
    version_blob_id: Optional[str]
    icon_uploaded: bool
    icon_blob_id: Optional[str]
    metadata_file_path: str


def get_metadata_remote_file_path(dockerRepository: str, version: str) -> str:
    """Get the path to the metadata file for a specific version of a connector.

    Args:
        dockerRepository (str): Name of the connector docker image.
        version (str): Version of the connector.
    Returns:
        str: Path to the metadata file.
    """
    return f"{METADATA_FOLDER}/{dockerRepository}/{version}/{METADATA_FILE_NAME}"


def get_icon_remote_file_path(dockerRepository: str, version: str) -> str:
    """Get the path to the icon file for a specific version of a connector.

    Args:
        dockerRepository (str): Name of the connector docker image.
        version (str): Version of the connector.
    Returns:
        str: Path to the icon file.
    """
    return f"{METADATA_FOLDER}/{dockerRepository}/{version}/{ICON_FILE_NAME}"


def compute_gcs_md5(file_name: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return base64.b64encode(hash_md5.digest()).decode("utf8")


def _save_blob_to_gcs(blob_to_save: storage.blob.Blob, file_path: str, disable_cache: bool = False) -> bool:
    """Uploads a file to the bucket."""
    print(f"Uploading {file_path} to {blob_to_save.name}...")

    # Set Cache-Control header to no-cache to avoid caching issues
    # This is IMPORTANT because if we don't set this header, the metadata file will be cached by GCS
    # and the next time we try to download it, we will get the stale version
    if disable_cache:
        blob_to_save.cache_control = "no-cache"

    blob_to_save.upload_from_filename(file_path)

    return True


def upload_file_if_changed(
    local_file_path: Path, bucket: storage.bucket.Bucket, blob_path: str, disable_cache: bool = False
) -> Tuple[bool, str]:
    local_file_md5_hash = compute_gcs_md5(local_file_path)
    remote_blob = bucket.blob(blob_path)

    # reload the blob to get the md5_hash
    if remote_blob.exists():
        remote_blob.reload()

    remote_blob_md5_hash = remote_blob.md5_hash if remote_blob.exists() else None

    print(f"Local {local_file_path} md5_hash: {local_file_md5_hash}")
    print(f"Remote {blob_path} md5_hash: {remote_blob_md5_hash}")

    if local_file_md5_hash != remote_blob_md5_hash:
        uploaded = _save_blob_to_gcs(remote_blob, local_file_path, disable_cache=disable_cache)
        return uploaded, remote_blob.id

    return False, remote_blob.id


def _latest_upload(metadata: ConnectorMetadataDefinitionV0, bucket: storage.bucket.Bucket, metadata_file_path: Path) -> Tuple[bool, str]:
    latest_path = get_metadata_remote_file_path(metadata.data.dockerRepository, "latest")
    return upload_file_if_changed(metadata_file_path, bucket, latest_path, disable_cache=True)


def _version_upload(metadata: ConnectorMetadataDefinitionV0, bucket: storage.bucket.Bucket, metadata_file_path: Path) -> Tuple[bool, str]:
    version_path = get_metadata_remote_file_path(metadata.data.dockerRepository, metadata.data.dockerImageTag)
    return upload_file_if_changed(metadata_file_path, bucket, version_path, disable_cache=True)


def _icon_upload(metadata: ConnectorMetadataDefinitionV0, bucket: storage.bucket.Bucket, metadata_file_path: Path) -> Tuple[bool, str]:
    local_icon_path = metadata_file_path.parent / ICON_FILE_NAME
    latest_icon_path = get_icon_remote_file_path(metadata.data.dockerRepository, "latest")
    if not local_icon_path.exists():
        return False, f"No Icon found at {local_icon_path}"
    return upload_file_if_changed(local_icon_path, bucket, latest_icon_path)


def create_prerelease_metadata_file(metadata_file_path: Path, prerelease_tag: str) -> Path:
    metadata, error = validate_and_load(metadata_file_path, [])
    if metadata is None:
        raise ValueError(f"Metadata file {metadata_file_path} is invalid for uploading: {error}")

    # replace any dockerImageTag references with the actual tag
    # this includes metadata.data.dockerImageTag, metadata.data.registries[].dockerImageTag
    # where registries is a dictionary of registry name to registry object
    metadata_dict = to_json_sanitized_dict(metadata, exclude_none=True)
    metadata_dict["data"]["dockerImageTag"] = prerelease_tag
    for registry in get(metadata_dict, "data.registries", {}).values():
        if "dockerImageTag" in registry:
            registry["dockerImageTag"] = prerelease_tag

    # write metadata to yaml file in system tmp folder
    tmp_metadata_file_path = Path("/tmp") / metadata.data.dockerRepository / prerelease_tag / METADATA_FILE_NAME
    tmp_metadata_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp_metadata_file_path, "w") as f:
        yaml.dump(metadata_dict, f)

    return tmp_metadata_file_path


def upload_metadata_to_gcs(bucket_name: str, metadata_file_path: Path, prerelease: Optional[str] = None) -> MetadataUploadInfo:
    """Upload a metadata file to a GCS bucket.

    If the per 'version' key already exists it won't be overwritten.
    Also updates the 'latest' key on each new version.

    Args:
        bucket_name (str): Name of the GCS bucket to which the metadata file will be uploade.
        metadata_file_path (Path): Path to the metadata file.
        service_account_file_path (Path): Path to the JSON file with the service account allowed to read and write on the bucket.
        prerelease (Optional[str]): Whether the connector is a prerelease or not.
    Returns:
        Tuple[bool, str]: Whether the metadata file was uploaded and its blob id.
    """
    if prerelease:
        metadata_file_path = create_prerelease_metadata_file(metadata_file_path, prerelease)

    metadata, error = validate_and_load(metadata_file_path, POST_UPLOAD_VALIDATORS)

    if metadata is None:
        raise ValueError(f"Metadata file {metadata_file_path} is invalid for uploading: {error}")

    service_account_info = json.loads(os.environ.get("GCS_CREDENTIALS"))
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)

    icon_uploaded, icon_blob_id = _icon_upload(metadata, bucket, metadata_file_path)

    version_uploaded, version_blob_id = _version_upload(metadata, bucket, metadata_file_path)
    if not prerelease:
        latest_uploaded, latest_blob_id = _latest_upload(metadata, bucket, metadata_file_path)
    else:
        latest_uploaded, latest_blob_id = False, None

    return MetadataUploadInfo(
        uploaded=version_uploaded or latest_uploaded,
        latest_uploaded=latest_uploaded,
        version_uploaded=version_uploaded,
        version_blob_id=version_blob_id,
        latest_blob_id=latest_blob_id,
        icon_blob_id=icon_blob_id,
        icon_uploaded=icon_uploaded,
        metadata_file_path=str(metadata_file_path),
    )
