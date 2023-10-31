#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import json
import logging
import re
from datetime import datetime
from io import IOBase
from typing import Any, Dict, Iterable, List, Optional, Set

from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType
from google.oauth2 import credentials, service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from .spec import SourceGoogleDriveSpec

FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
GOOGLE_DOC_MIME_TYPE = "application/vnd.google-apps.document"
EXPORTABLE_DOCUMENTS_MIME_TYPES = [
    GOOGLE_DOC_MIME_TYPE,
    "application/vnd.google-apps.presentation",
    "application/vnd.google-apps.drawing",
]


class GoogleDriveRemoteFile(RemoteFile):
    id: str
    mimeType: str


class SourceGoogleDriveStreamReader(AbstractFileBasedStreamReader):
    def __init__(self):
        super().__init__()
        self._drive_service = None

    @property
    def config(self) -> SourceGoogleDriveSpec:
        return self._config

    @config.setter
    def config(self, value: SourceGoogleDriveSpec):
        """
        FileBasedSource reads the config from disk and parses it, and once parsed, the source sets the config on its StreamReader.

        Note: FileBasedSource only requires the keys defined in the abstract config, whereas concrete implementations of StreamReader
        will require keys that (for example) allow it to authenticate with the 3rd party.

        Therefore, concrete implementations of AbstractFileBasedStreamReader's config setter should assert that `value` is of the correct
        config type for that type of StreamReader.
        """
        assert isinstance(value, SourceGoogleDriveSpec)
        self._config = value

    @property
    def google_drive_service(self):
        if self.config is None:
            # We shouldn't hit this; config should always get set before attempting to
            # list or read files.
            raise ValueError("Source config is missing; cannot create the Google Drive client.")
        try:
            if self._drive_service is None:
                if self.config.credentials.auth_type == "Client":
                    creds = credentials.Credentials.from_authorized_user_info(self.config.credentials.dict())
                else:
                    creds = service_account.Credentials.from_service_account_info(json.loads(self.config.credentials.service_account_info))
                self._drive_service = build("drive", "v3", credentials=creds)
        except Exception as e:
            raise AirbyteTracedException(
                internal_message=str(e),
                message="Could not authenticate with Google Drive. Please check your credentials.",
                failure_type=FailureType.config_error,
                exception=e,
            )

        return self._drive_service

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Get all files matching the specified glob patterns.
        """
        service = self.google_drive_service
        root_folder_id = self._get_folder_id(self.config.folder_url)
        # ignore prefix argument as it's legacy only and this is a new connector
        prefixes = self.get_prefixes_from_globs(globs)

        folder_id_queue = [("", root_folder_id)]
        seen: Set[str] = set()
        while len(folder_id_queue) > 0:
            (path, folder_id) = folder_id_queue.pop()
            # fetch all files in this folder (1000 is the max page size)
            request = service.files().list(
                q=f"'{folder_id}' in parents", pageSize=1000, fields="nextPageToken, files(id, name, modifiedTime, mimeType)"
            )
            while True:
                results = request.execute()
                new_files = results.get("files", [])
                for new_file in new_files:
                    # It's possible files and folders are linked up multiple times, this prevents us from getting stuck in a loop
                    if new_file["id"] in seen:
                        continue
                    seen.add(new_file["id"])
                    file_name = path + self._get_file_name(new_file)
                    if new_file["mimeType"] == FOLDER_MIME_TYPE:
                        folder_name = f"{file_name}/"
                        # check prefix matching in both directions to handle
                        prefix_matches_folder_name = any(prefix.startswith(folder_name) for prefix in prefixes)
                        folder_name_matches_prefix = any(folder_name.startswith(prefix) for prefix in prefixes)
                        if prefix_matches_folder_name or folder_name_matches_prefix or len(prefixes) == 0:
                            folder_id_queue.append((folder_name, new_file["id"]))
                        continue
                    else:
                        last_modified = datetime.strptime(new_file["modifiedTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
                        remote_file = GoogleDriveRemoteFile(
                            uri=file_name, last_modified=last_modified, id=new_file["id"], mimeType=new_file["mimeType"]
                        )
                        if self.file_matches_globs(remote_file, globs):
                            yield remote_file
                request = service.files().list_next(request, results)
                if request is None:
                    break

    def _get_folder_id(self, url):
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

    def _is_exportable_document(self, mime_type: str):
        """
        Returns true if the given file is a Google App document that can be exported.
        """
        return mime_type in EXPORTABLE_DOCUMENTS_MIME_TYPES

    def _get_file_name(self, file: Dict[str, Any]):
        """
        Returns the file name for the given file.

        Google Docs are exported as Docx to preserve as much formatting as possible, other google app documents are exported as PDFs.
        For all other files, the file name is returned as is.
        """
        if file["mimeType"] == GOOGLE_DOC_MIME_TYPE:
            return f"{file['name']}.docx"
        elif self._is_exportable_document(file["mimeType"]):
            return f"{file['name']}.pdf"
        else:
            return file["name"]

    def open_file(self, file: GoogleDriveRemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        if self._is_exportable_document(file.mimeType):
            if mode == FileReadMode.READ:
                raise ValueError(
                    "Google Docs/Drawings/Presentations can only be processed using the document file type format. Please set the format accordingly or adjust the glob pattern."
                )
            request = self.google_drive_service.files().export_media(fileId=file.id, mimeType=self._get_export_mime_type(file))
        else:
            request = self.google_drive_service.files().get_media(fileId=file.id)
        handle = io.BytesIO()
        downloader = MediaIoBaseDownload(handle, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

        handle.seek(0)

        if mode == FileReadMode.READ_BINARY:
            return handle
        else:
            # repack the bytes into a string with the right encoding
            text_handle = io.StringIO(handle.read().decode(encoding or "utf-8"))
            handle.close()
            return text_handle

    def _get_export_mime_type(self, file: GoogleDriveRemoteFile):
        """
        Returns the mime type to export Google App documents as.

        Google Docs are exported as Docx to preserve as much formatting as possible, everything else goes through PDF.
        """
        if file.mimeType.startswith(GOOGLE_DOC_MIME_TYPE):
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            return "application/pdf"
