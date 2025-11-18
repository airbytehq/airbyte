#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import os
from typing import Optional

from google.cloud import storage
from google.oauth2 import service_account


def get_gcs_storage_client(gcs_creds: Optional[str] = None) -> storage.Client:
    """Get the GCS storage client using credentials form GCS_CREDENTIALS env variable."""
    gcs_creds = os.environ.get("GCS_CREDENTIALS") if not gcs_creds else gcs_creds
    if not gcs_creds:
        raise ValueError("Please set the GCS_CREDENTIALS env var.")

    service_account_info = json.loads(gcs_creds)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    return storage.Client(credentials=credentials)


def safe_read_gcs_file(gcs_blob: storage.Blob) -> Optional[str]:
    """Read the connector metrics jsonl blob.

    Args:
        gcs_blob (storage.Blob): The blob.

    Returns:
        dict: The metrics.
    """
    if not gcs_blob.exists():
        return None

    return gcs_blob.download_as_string().decode("utf-8")


def is_version_yanked(bucket: storage.Bucket, docker_repository: str, version: str) -> bool:
    """Check if a specific connector version has been yanked.

    A version is considered yanked if a .yanked marker file exists in its GCS directory.

    Args:
        bucket (storage.Bucket): The GCS bucket.
        docker_repository (str): The docker repository (e.g., 'airbyte/source-postgres').
        version (str): The version to check (e.g., '3.7.0').

    Returns:
        bool: True if the version is yanked, False otherwise.
    """
    from metadata_service.constants import METADATA_FOLDER

    yank_marker_path = f"{METADATA_FOLDER}/{docker_repository}/{version}/.yanked"
    yank_marker_blob = bucket.blob(yank_marker_path)
    return yank_marker_blob.exists()
