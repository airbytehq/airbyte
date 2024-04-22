#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import itertools
import json
import logging
from datetime import datetime, timedelta
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
        self._config = None

    @property
    def config(self) -> Config:
        return self._config

    @config.setter
    def config(self, value: Config):
        assert isinstance(value, Config), "Config must be an instance of the expected Config class."
        self._config = value

    def _initialize_gcs_client(self):
        if self.config is None:
            raise ValueError("Source config is missing; cannot create the GCS client.")
        if self._gcs_client is None:
            credentials = self._get_credentials()
            self._gcs_client = storage.Client(credentials=credentials)
        return self._gcs_client

    def _get_credentials(self):
        return service_account.Credentials.from_service_account_info(json.loads(self.config.service_account))

    @property
    def gcs_client(self) -> storage.Client:
        return self._initialize_gcs_client()

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Retrieve all files matching the specified glob patterns in GCS.
        """
        try:
            start_date = (
                datetime.strptime(self.config.start_date, self.DATE_TIME_FORMAT) if self.config and self.config.start_date else None
            )
            prefixes = [prefix] if prefix else self.get_prefixes_from_globs(globs or [])
            globs = globs or [None]

            for prefix, glob in itertools.product(prefixes, globs):
                bucket = self.gcs_client.get_bucket(self.config.bucket)
                blobs = bucket.list_blobs(prefix=prefix, match_glob=glob)
                for blob in blobs:
                    last_modified = blob.updated.astimezone(pytz.utc).replace(tzinfo=None)

                    if FILE_FORMAT in blob.name.lower() and (not start_date or last_modified >= start_date):
                        uri = blob.generate_signed_url(expiration=timedelta(hours=1), version="v4")

                        file_extension = ".".join(blob.name.split(".")[1:])

                        yield RemoteFile(uri=uri, last_modified=last_modified, mime_type=file_extension)

        except Exception as exc:
            self._handle_file_listing_error(exc, prefix, logger)

    def _handle_file_listing_error(self, exc: Exception, prefix: str, logger: logging.Logger):
        logger.error(f"Error while listing files: {str(exc)}")
        raise ErrorListingFiles(
            FileBasedSourceError.ERROR_LISTING_FILES,
            source="gcs",
            bucket=self.config.bucket,
            prefix=prefix,
        ) from exc

    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        """
        Open and yield a remote file from GCS for reading.
        """
        logger.debug(f"Trying to open {file.uri}")

        # choose correct compression mode
        file_extension = file.mime_type.split(".")[-1]
        if file_extension in ["gz", "bz2"]:
            compression = "." + file_extension
        else:
            compression = "disable"

        try:
            result = smart_open.open(file.uri, mode=mode.value, compression=compression, encoding=encoding)
        except OSError as oe:
            logger.warning(ERROR_MESSAGE_ACCESS.format(uri=file.uri, bucket=self.config.bucket))
            logger.exception(oe)
        return result
