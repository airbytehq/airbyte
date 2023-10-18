#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import json
import logging
import re
from contextlib import contextmanager
from datetime import datetime
from io import IOBase
from typing import Any, Iterable, List, Optional, Set

import boto3.session
import pytz
import smart_open
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources.file_based.exceptions import ErrorListingFiles, FileBasedSourceError
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from botocore.client import BaseClient
from botocore.client import Config as ClientConfig
from google.auth.transport.requests import Request
from google.oauth2 import credentials, service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from .spec import SourceGoogleDriveSpec as Config


class SourceGoogleDriveStreamReader(AbstractFileBasedStreamReader):
    def __init__(self):
        super().__init__()
        self._drive_service = None

    @property
    def config(self) -> Config:
        return self._config

    @config.setter
    def config(self, value: Config):
        """
        FileBasedSource reads the config from disk and parses it, and once parsed, the source sets the config on its StreamReader.

        Note: FileBasedSource only requires the keys defined in the abstract config, whereas concrete implementations of StreamReader
        will require keys that (for example) allow it to authenticate with the 3rd party.

        Therefore, concrete implementations of AbstractFileBasedStreamReader's config setter should assert that `value` is of the correct
        config type for that type of StreamReader.
        """
        assert isinstance(value, Config)
        self._config = value

    @property
    def google_drive_service(self) -> BaseClient:
        if self.config is None:
            # We shouldn't hit this; config should always get set before attempting to
            # list or read files.
            raise ValueError("Source config is missing; cannot create the Google Drive client.")
        if self._drive_service is None:
            if self.config.credentials.auth_type == "Client":
                creds = credentials.Credentials.from_authorized_user_info(self.config.credentials.dict())
            else:
                creds = service_account.Credentials.from_service_account_info(json.loads(self.config.credentials.service_account_info))
            self._drive_service = build("drive", "v3", credentials=creds)
        return self._drive_service

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Get all files matching the specified glob patterns.
        """
        service = self.google_drive_service
        folder_id = self.get_folder_id(self.config.folder_url)

        request = service.files().list(q=f"'{folder_id}' in parents", pageSize=10, fields="nextPageToken, files(id, name, modifiedTime)")
        while True:
            results = request.execute()
            new_files = results.get("files", [])
            for new_file in new_files:
                last_modified = datetime.strptime(new_file["modifiedTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
                remote_file = RemoteFile(uri=new_file["name"], last_modified=last_modified)
                if self.file_matches_globs(remote_file, globs):
                    # the glob matching operates on file names, but google drive uses auto-generated ids. So rewrite the RemoteFile instance after it matched
                    yield RemoteFile(uri=self.get_uri(new_file["id"]), last_modified=last_modified)
            request = service.files().list_next(request, results)
            if request is None:
                break

    def get_uri(self, id: str):
        return f"https://drive.google.com/file/d/{id}"

    def get_file_id(self, url):
        # Regular expression pattern to check the URL structure and extract the ID
        pattern = r"^https://drive\.google\.com/file/d/(.+)$"

        # Find the pattern in the URL
        match = re.search(pattern, url)

        if match:
            # The matched group is the ID
            drive_id = match.group(1)
            return drive_id
        else:
            # If no match is found
            raise ValueError(f"Could not extract file ID from {url}")

    def get_folder_id(self, url):
        # Regular expression pattern to check the URL structure and extract the ID
        pattern = r"^https://drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)$"

        # Find the pattern in the URL
        match = re.search(pattern, url)

        if match:
            # The matched group is the ID
            drive_id = match.group(1)
            return drive_id
        else:
            # If no match is found
            raise ValueError(f"Could not extract folder ID from {url}")

    @contextmanager
    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:

        request = self.google_drive_service.files().get_media(fileId=self.get_file_id(file.uri))
        handle = io.BytesIO()
        downloader = MediaIoBaseDownload(handle, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        handle.seek(0)

        if mode == FileReadMode.READ_BINARY:
            try:
                yield handle
            finally:
                handle.close()
        else:
            # repack the bytes into a string with the right encoding
            try:
                text_handle = io.StringIO(handle.read().decode(encoding))
                yield text_handle
            finally:
                text_handle.close()
                handle.close()
