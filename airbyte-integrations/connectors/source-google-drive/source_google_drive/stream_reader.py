#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import json
import logging
import re
from datetime import datetime
from io import IOBase
from typing import Iterable, List, Optional, Set

from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from google.oauth2 import credentials, service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient._apis.drive.v3.resources import DriveResource

from .spec import SourceGoogleDriveSpec as Config

FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
DOC_MIME_TYPE_PREFIX = "application/vnd.google-apps."


class GoogleDriveRemoteFile(RemoteFile):
    id: str
    mimeType: str


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
    def google_drive_service(self) -> DriveResource:
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
        root_folder_id = self.get_folder_id(self.config.folder_url)

        folder_id_queue = [("/", root_folder_id)]
        seen: Set[str] = set()
        while len(folder_id_queue) > 0:
            (path, folder_id) = folder_id_queue.pop()
            request = service.files().list(
                q=f"'{folder_id}' in parents", pageSize=10, fields="nextPageToken, files(id, name, modifiedTime, mimeType)"
            )
            while True:
                results = request.execute()
                new_files = results.get("files", [])
                for new_file in new_files:
                    # It's possible files and folders are linked up multiple times, this prevents us from getting stuck in a loop
                    if new_file["id"] in seen:
                        continue
                    seen.add(new_file["id"])
                    file_name = path + new_file["name"]
                    if new_file["mimeType"] == FOLDER_MIME_TYPE:
                        folder_id_queue.append((f"{file_name}/", new_file["id"]))
                        continue
                    last_modified = datetime.strptime(new_file["modifiedTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    remote_file = GoogleDriveRemoteFile(
                        uri=file_name, last_modified=last_modified, id=new_file["id"], mimeType=new_file["mimeType"]
                    )
                    print(remote_file)
                    if self.file_matches_globs(remote_file, globs):
                        yield remote_file
                request = service.files().list_next(request, results)
                if request is None:
                    break

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

    def open_file(self, file: GoogleDriveRemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        if file.mimeType.startswith(DOC_MIME_TYPE_PREFIX):
            if mode == FileReadMode.READ:
                raise ValueError("Cannot read Google Docs/Sheets/Presentations and so on as text. Please set the format to PDF")
            request = self.google_drive_service.files().export_media(fileId=file.id, mimeType="application/pdf")
        else:
            request = self.google_drive_service.files().get_media(fileId=file.id)
        handle = io.BytesIO()
        downloader = MediaIoBaseDownload(handle, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        handle.seek(0)

        if mode == FileReadMode.READ_BINARY:
            return handle
        else:
            # repack the bytes into a string with the right encoding
            text_handle = io.StringIO(handle.read().decode(encoding))
            handle.close()
            return text_handle
