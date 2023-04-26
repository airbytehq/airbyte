#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pathlib import Path
from typing import Tuple

import yaml
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


def upload_metadata_to_gcs(bucket_name: str, metadata_file_path: Path, service_account_file_path: Path) -> Tuple[bool, str]:
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

    # Validate that the images are on DockerHub
    is_valid, error = validate_metadata_images_in_dockerhub(metadata)
    if not is_valid:
        raise ValueError(error)

    credentials = service_account.Credentials.from_service_account_file(service_account_file_path)
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)

    version_path = get_metadata_file_path(metadata.data.dockerRepository, metadata.data.dockerImageTag)
    latest_path = get_metadata_file_path(metadata.data.dockerRepository, "latest")

    version_blob = bucket.blob(version_path)
    latest_blob = bucket.blob(latest_path)
    if not version_blob.exists():
        version_blob.upload_from_filename(str(metadata_file_path))
        uploaded = True
    if version_blob.etag != latest_blob.etag:
        latest_blob.upload_from_filename(str(metadata_file_path))
    return uploaded, version_blob.id
