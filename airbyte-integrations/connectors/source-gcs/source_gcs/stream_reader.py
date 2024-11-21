#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import itertools
import json
import logging
import tempfile
from datetime import datetime, timedelta
from io import IOBase
from typing import Iterable, List, Optional

import pytz
import smart_open
from airbyte_cdk.sources.file_based.exceptions import ErrorListingFiles, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from google.cloud import storage
from google.oauth2 import credentials, service_account
from source_gcs.config import Config
from source_gcs.helpers import GCSRemoteFile
from source_gcs.zip_helper import ZipHelper

# google can raise warnings for end user credentials, wrapping it to Logger
logging.captureWarnings(True)

ERROR_MESSAGE_ACCESS = (
    "We don't have access to {uri}. The file appears to have become unreachable during sync."
    "Check whether key {uri} exists in `{bucket}` bucket and/or has proper ACL permissions"
)


class SourceGCSStreamReader(AbstractFileBasedStreamReader):
    """
    Stream reader for Google Cloud Storage (GCS).
    """

    def __init__(self):
        super().__init__()
        self._gcs_client = None
        self._config = None
        self.tmp_dir = tempfile.TemporaryDirectory()

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
            # using default project to avoid getting project from env, applies only for OAuth creds
            project = getattr(credentials, "project_id", "default")
            self._gcs_client = storage.Client(project=project, credentials=credentials)
        return self._gcs_client

    def _get_credentials(self):
        if self.config.credentials.auth_type == "Service":
            # Service Account authorization
            return service_account.Credentials.from_service_account_info(json.loads(self.config.credentials.service_account))
        # Google OAuth
        return credentials.Credentials(
            self.config.credentials.access_token,
            refresh_token=self.config.credentials.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.config.credentials.client_id,
            client_secret=self.config.credentials.client_secret,
        )

    @property
    def gcs_client(self) -> storage.Client:
        return self._initialize_gcs_client()

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[GCSRemoteFile]:
        """
        Retrieve all files matching the specified glob patterns in GCS.
        """
        try:
            start_date = (
                datetime.strptime(self.config.start_date, self.DATE_TIME_FORMAT) if self.config and self.config.start_date else None
            )
            prefixes = [prefix] if prefix else self.get_prefixes_from_globs(globs or [])
            globs = globs or [None]

            if not prefixes:
                prefixes = [""]

            for prefix, glob in itertools.product(prefixes, globs):
                bucket = self.gcs_client.get_bucket(self.config.bucket)
                blobs = bucket.list_blobs(prefix=prefix, match_glob=glob)
                for blob in blobs:
                    last_modified = blob.updated.astimezone(pytz.utc).replace(tzinfo=None)

                    if not start_date or last_modified >= start_date:

                        if self.config.credentials.auth_type == "Client":
                            uri = f"gs://{blob.bucket.name}/{blob.name}"
                        else:
                            uri = blob.generate_signed_url(expiration=timedelta(days=7), version="v4")

                        file_extension = ".".join(blob.name.split(".")[1:])
                        remote_file = GCSRemoteFile(uri=uri, last_modified=last_modified, mime_type=file_extension)

                        if file_extension == "zip":
                            yield from ZipHelper(blob, remote_file, self.tmp_dir).get_gcs_remote_files()
                        else:
                            yield remote_file
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

    def open_file(self, file: GCSRemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
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
            result = smart_open.open(
                file.uri, mode=mode.value, compression=compression, encoding=encoding, transport_params={"client": self.gcs_client}
            )
        except OSError as oe:
            logger.warning(ERROR_MESSAGE_ACCESS.format(uri=file.uri, bucket=self.config.bucket))
            logger.exception(oe)
            raise oe
        return result
