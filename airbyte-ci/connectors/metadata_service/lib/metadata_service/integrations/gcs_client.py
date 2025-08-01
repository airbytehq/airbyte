#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import json
import logging
import os
from pathlib import Path
from typing import NamedTuple, Optional

from google.cloud import storage
from google.oauth2 import service_account

from metadata_service.helpers.files import compute_gcs_md5

logger = logging.getLogger(__name__)


class UploadResult(NamedTuple):
    uploaded: bool
    blob_id: str


class GCSClient:
    """
    A client for interacting with Google Cloud Storage.

    This class encapsulates basic GCS operations and manages authentication
    and bucket access.
    """

    def __init__(self, bucket_name: str, gcs_credentials: Optional[str] = None):
        """
        Initialize the GCS client.

        Args:
            bucket_name: Name of the GCS bucket
            gcs_credentials: GCS credentials JSON string. If None, uses GCS_CREDENTIALS env var
        """
        self.bucket_name = bucket_name
        self._storage_client = self._create_storage_client(gcs_credentials)
        self._bucket: Optional[storage.Bucket] = None

    def _create_storage_client(self, gcs_credentials: Optional[str]) -> storage.Client:
        """Create and return a GCS storage client."""
        creds = gcs_credentials or os.environ.get("GCS_CREDENTIALS")
        if not creds:
            raise ValueError("GCS credentials are required. Set GCS_CREDENTIALS env var or pass credentials explicitly.")

        service_account_info = json.loads(creds)
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        return storage.Client(credentials=credentials)

    @property
    def bucket(self) -> storage.Bucket:
        if self._bucket is None:
            logger.info(f"Connecting to GCS bucket: {self.bucket_name}")
            self._bucket = self._storage_client.bucket(self.bucket_name)
        return self._bucket

    def get_blob_id(self, blob_path: str) -> str:
        """Get a blob from GCS."""
        return self.bucket.blob(blob_path).id

    def blob_exists(self, blob_path: str) -> bool:
        """Check if a blob exists in GCS."""
        return self.bucket.blob(blob_path).exists()

    def delete_blob(self, blob_path: str) -> bool:
        """Delete a blob from GCS."""
        blob = self.bucket.blob(blob_path)
        if blob.exists():
            blob.delete()
            return True
        return False

    def copy_blob(self, source_blob_path: str, destination_blob_path: str) -> bool:
        """Copy a blob from GCS."""
        source_blob = self.bucket.blob(source_blob_path)
        destination_blob = self.bucket.blob(destination_blob_path)
        destination_blob.copy_from(source_blob)
        return True

    def get_blob_md5(self, blob_path: str) -> Optional[str]:
        """Get the MD5 hash of a blob."""
        blob = self.bucket.blob(blob_path)
        if blob.exists():
            blob.reload()
            return blob.md5_hash
        return None

    def upload_file(
        self,
        local_file_path: Path,
        blob_path: str,
        disable_cache: bool = False,
        overwrite: bool = True
    ) -> bool:
        """
        Upload a blob to GCS.

        Args:
            local_file_path: Path to the local file
            blob_path: Destination path in GCS
            disable_cache: Whether to disable caching
            overwrite: Whether to overwrite existing files

        Returns:
            True if file was uploaded, False if skipped
        """
        if not local_file_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_file_path}")

        blob = self.bucket.blob(blob_path)

        if not overwrite and blob.exists():
            logger.info(f"Blob {blob_path} already exists, skipping upload")
            return False

        logger.info(f"Uploading {local_file_path} to {blob_path}")

        # Set Cache-Control header to no-cache to avoid caching issues
        # This is IMPORTANT because if we don't set this header, the file will be cached by GCS
        # and the next time we try to download it, we will get the stale version
        if disable_cache:
            blob.cache_control = "no-cache"

        blob.upload_from_filename(local_file_path)
        return True

    def upload_file_if_changed(
        self,
        local_file_path: Path,
        blob_path: str,
        disable_cache: bool = False
    ) -> UploadResult:
        """
        Upload a file to GCS only if it has changed.

        Returns:
            UploadResult
        """
        local_file_md5_hash = compute_gcs_md5(local_file_path)

        remote_blob = self.bucket.blob(blob_path)
        remote_blob_md5_hash = self.get_blob_md5(blob_path)

        print(f"Local {local_file_path} md5_hash: {local_file_md5_hash}")
        print(f"Remote {blob_path} md5_hash: {remote_blob_md5_hash}")

        if local_file_md5_hash != remote_blob_md5_hash:
            uploaded = self.upload_file(local_file_path, blob_path, disable_cache=disable_cache)
            return UploadResult(uploaded=uploaded, blob_id=remote_blob.id)

        return UploadResult(uploaded=False, blob_id=remote_blob.id)
