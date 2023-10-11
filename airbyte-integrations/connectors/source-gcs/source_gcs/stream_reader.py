#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from contextlib import contextmanager
from datetime import timedelta
from io import IOBase
from typing import Iterable, List, Optional

import pytz
import smart_open
from airbyte_cdk.sources.file_based.exceptions import ErrorListingFiles, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from google.cloud import storage
from google.oauth2 import service_account
from source_gcs.config import Config

ERROR_MESSAGE_ACCESS = (
    "We don't have access to {uri}. The file appears to have become unreachable during sync."
    "Check whether key {uri} exists in `{bucket}` bucket and/or has proper ACL permissions"
)
FILE_FORMAT = "csv"  # TODO: Change if other file formats are implemented


class SourceGCSStreamReader(AbstractFileBasedStreamReader):
    """
    Stream reader for Google Cloud Storage (GCS).
    """

    def __init__(self):
        super().__init__()
        self._gcs_client = None

    @property
    def config(self) -> Config:
        return self._config

    @config.setter
    def config(self, value: Config):
        assert isinstance(value, Config), "Config must be an instance of the expected Config class."
        self._config = value

    @property
    def gcs_client(self) -> storage.Client:
        if self.config is None:
            raise ValueError("Source config is missing; cannot create the GCS client.")
        if self._gcs_client is None:
            credentials = service_account.Credentials.from_service_account_info(json.loads(self.config.service_account))
            self._gcs_client = storage.Client(credentials=credentials)
        return self._gcs_client

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Retrieve all files matching the specified glob patterns in GCS.
        """
        try:
            bucket = self.gcs_client.get_bucket(self.config.bucket)
            remote_files = bucket.list_blobs(prefix=prefix)

            for remote_file in remote_files:
                if FILE_FORMAT in remote_file.name.lower():
                    yield RemoteFile(
                        uri=remote_file.generate_signed_url(expiration=timedelta(hours=1), version="v4"),
                        last_modified=remote_file.updated.astimezone(pytz.utc).replace(tzinfo=None),
                    )

        except Exception as exc:
            logger.error(f"Error while listing files: {str(exc)}")
            raise ErrorListingFiles(
                FileBasedSourceError.ERROR_LISTING_FILES,
                source="gcs",
                bucket=self.config.bucket,
                prefix=prefix,
            ) from exc

    @contextmanager
    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        """
        Open and yield a remote file from GCS for reading.
        """
        logger.debug(f"Trying to open {file.uri}")
        try:
            result = smart_open.open(file.uri, mode=mode.value, encoding=encoding)
        except OSError as oe:
            logger.warning(ERROR_MESSAGE_ACCESS.format(uri=file.uri, bucket=self.config.bucket))
            logger.exception(oe)
        try:
            yield result
        finally:
            result.close()
