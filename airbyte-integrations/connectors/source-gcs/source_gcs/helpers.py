#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import urllib.parse
from datetime import timedelta
from typing import Any

import pytz
from google.cloud import storage
from google.oauth2 import credentials, service_account

from airbyte_cdk.sources.file_based.remote_file import UploadableRemoteFile


def get_gcs_client(config):
    if config.credentials.auth_type == "Service":
        creds = service_account.Credentials.from_service_account_info(json.loads(config.credentials.service_account))
    else:
        creds = credentials.Credentials(
            config.credentials.access_token,
            refresh_token=config.credentials.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=config.credentials.client_id,
            client_secret=config.credentials.client_secret,
        )
    client = storage.Client(credentials=creds)
    return client


def get_gcs_blobs(config):
    client = get_gcs_client(config)
    bucket = client.get_bucket(config.gcs_bucket)
    blobs = bucket.list_blobs(prefix=config.gcs_path)
    # TODO: only support CSV initially. Change this check if implementing other file formats.
    blobs = [blob for blob in blobs if "csv" in blob.name.lower()]
    return blobs


def get_stream_name(blob):
    blob_name = blob.name
    # Remove path from stream name
    blob_name_without_path = blob_name.split("/")[-1]
    # Remove file extension from stream name
    stream_name = blob_name_without_path.replace(".csv", "")
    return stream_name


class GCSUploadableRemoteFile(UploadableRemoteFile):
    """
    Extends RemoteFile instance with displayed_uri attribute.
    displayed_uri is being used by Cursor to identify files with temporal local path in their uri attribute.
    """

    blob: Any
    displayed_uri: str = None

    def __init__(self, blob: Any, displayed_uri: str = None, **kwargs):
        super().__init__(**kwargs)
        self.blob = blob
        self.displayed_uri = displayed_uri
        self.id = self.blob.id
        self.created_at = self.blob.time_created.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.updated_at = self.blob.updated.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @property
    def size(self) -> int:
        return self.blob.size

    def download_to_local_directory(self, local_file_path: str) -> None:
        self.blob.download_to_filename(local_file_path)

    @property
    def source_file_relative_path(self) -> str:
        return urllib.parse.unquote(self.blob.path)

    @property
    def file_uri_for_logging(self) -> str:
        return urllib.parse.unquote(self.blob.path)
