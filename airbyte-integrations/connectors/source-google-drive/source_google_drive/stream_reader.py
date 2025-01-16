#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import io
import json
import logging
from collections import defaultdict
from datetime import datetime
from io import IOBase
from typing import Dict, Iterable, List, Optional, Set

from google.oauth2 import credentials, service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.file_based.exceptions import FileSizeLimitError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from source_google_drive.utils import get_folder_id

from .spec import SourceGoogleDriveSpec


FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
GOOGLE_DOC_MIME_TYPE = "application/vnd.google-apps.document"
GOOGLE_PRESENTATION_MIME_TYPE = "application/vnd.google-apps.presentation"
GOOGLE_DRAWING_MIME_TYPE = "application/vnd.google-apps.drawing"
EXPORTABLE_DOCUMENTS_MIME_TYPES = [GOOGLE_DOC_MIME_TYPE, GOOGLE_PRESENTATION_MIME_TYPE, GOOGLE_DRAWING_MIME_TYPE]

EXPORT_MEDIA_MIME_TYPE_DOC = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
EXPORT_MEDIA_MIME_TYPE_SPREADSHEET = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
EXPORT_MEDIA_MIME_TYPE_PRESENTATION = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
EXPORT_MEDIA_MIME_TYPE_PDF = "application/pdf"

# This key is used to relate the required mimeType parameter for export_media() method
EXPORT_MEDIA_MIME_TYPE_KEY = "exportable_mime_type"
DOCUMENT_FILE_EXTENSION_KEY = "document_file_extension"

DOWNLOADABLE_DOCUMENTS_MIME_TYPES = defaultdict(
    lambda: {
        EXPORT_MEDIA_MIME_TYPE_KEY: EXPORT_MEDIA_MIME_TYPE_PDF,
        DOCUMENT_FILE_EXTENSION_KEY: ".pdf",
    },  # Default value for unsupported types
    {
        GOOGLE_DOC_MIME_TYPE: {EXPORT_MEDIA_MIME_TYPE_KEY: EXPORT_MEDIA_MIME_TYPE_DOC, DOCUMENT_FILE_EXTENSION_KEY: ".docx"},
        "application/vnd.google-apps.spreadsheet": {
            EXPORT_MEDIA_MIME_TYPE_KEY: EXPORT_MEDIA_MIME_TYPE_SPREADSHEET,
            DOCUMENT_FILE_EXTENSION_KEY: ".xlsx",
        },
        GOOGLE_PRESENTATION_MIME_TYPE: {
            EXPORT_MEDIA_MIME_TYPE_KEY: EXPORT_MEDIA_MIME_TYPE_PRESENTATION,
            DOCUMENT_FILE_EXTENSION_KEY: ".pptx",
        },
        GOOGLE_DRAWING_MIME_TYPE: {EXPORT_MEDIA_MIME_TYPE_KEY: EXPORT_MEDIA_MIME_TYPE_PDF, DOCUMENT_FILE_EXTENSION_KEY: ".pdf"},
    },
)


def get_file_extension(mime_type: str) -> str:
    extension_map = {}
    return extension_map.get(mime_type, ".bin")  # Default to `.bin` for unknown types


class GoogleDriveRemoteFile(RemoteFile):
    id: str
    # The mime type of the file as returned by the Google Drive API
    # This is not the same as the mime type when opened by the parser (e.g. google docs is exported as docx)
    original_mime_type: str


class SourceGoogleDriveStreamReader(AbstractFileBasedStreamReader):
    FILE_SIZE_LIMIT = 1_500_000_000

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
        root_folder_id = get_folder_id(self.config.folder_url)
        # ignore prefix argument as it's legacy only and this is a new connector
        prefixes = self.get_prefixes_from_globs(globs)

        folder_id_queue = [("", root_folder_id)]
        seen: Set[str] = set()
        while len(folder_id_queue) > 0:
            (path, folder_id) = folder_id_queue.pop()
            # fetch all files in this folder (1000 is the max page size)
            # supportsAllDrives and includeItemsFromAllDrives are required to access files in shared drives
            request = service.files().list(
                q=f"'{folder_id}' in parents",
                pageSize=1000,
                fields="nextPageToken, files(id, name, modifiedTime, mimeType)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
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
                        folder_name = f"{file_name}/"
                        # check prefix matching in both directions to handle
                        prefix_matches_folder_name = any(prefix.startswith(folder_name) for prefix in prefixes)
                        folder_name_matches_prefix = any(folder_name.startswith(prefix) for prefix in prefixes)
                        if prefix_matches_folder_name or folder_name_matches_prefix or len(prefixes) == 0:
                            folder_id_queue.append((folder_name, new_file["id"]))
                        continue
                    else:
                        last_modified = datetime.strptime(new_file["modifiedTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
                        original_mime_type = new_file["mimeType"]
                        mime_type = (
                            self._get_export_mime_type(original_mime_type)
                            if self._is_exportable_document(original_mime_type)
                            else original_mime_type
                        )
                        remote_file = GoogleDriveRemoteFile(
                            uri=file_name,
                            last_modified=last_modified,
                            id=new_file["id"],
                            original_mime_type=original_mime_type,
                            mime_type=mime_type,
                        )
                        if self.file_matches_globs(remote_file, globs):
                            yield remote_file
                request = service.files().list_next(request, results)
                if request is None:
                    break

    def _is_exportable_document(self, mime_type: str):
        """
        Returns true if the given file is a Google App document that can be exported.
        """
        return mime_type in EXPORTABLE_DOCUMENTS_MIME_TYPES

    def open_file(self, file: GoogleDriveRemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        if self._is_exportable_document(file.original_mime_type):
            if mode == FileReadMode.READ:
                raise ValueError(
                    "Google Docs/Drawings/Presentations can only be processed using the document file type format. Please set the format accordingly or adjust the glob pattern."
                )
            request = self.google_drive_service.files().export_media(fileId=file.id, mimeType=file.mime_type)
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

    def _get_export_mime_type(self, original_mime_type: str):
        """
        Returns the mime type to export Google App documents as.
        """
        if self.use_file_transfer():
            return DOWNLOADABLE_DOCUMENTS_MIME_TYPES[original_mime_type][EXPORT_MEDIA_MIME_TYPE_KEY]

        if original_mime_type.startswith(GOOGLE_DOC_MIME_TYPE):
            # Google Docs are exported as Docx to preserve as much formatting as possible, everything else goes through PDF.
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            return "application/pdf"

    def file_size(self, file: GoogleDriveRemoteFile) -> int:
        """
        Retrieves the size of a file in Google Drive.

        Args:
            file (RemoteFile): The file to get the size for.

        Returns:
            int: The file size in bytes.
        """
        try:
            file_metadata = self.google_drive_service.files().get(fileId=file.id, fields="size").execute()
            return int(file_metadata.get("size", 0))
        except Exception as e:
            # TODO: check why this is failing
            return 0
            # raise ValueError(f"Failed to retrieve file size for {file.id}: {e}")

    def get_file(self, file: GoogleDriveRemoteFile, local_directory: str, logger: logging.Logger) -> Dict[str, str | int]:
        """
        Downloads a file from Google Drive to a specified local directory.

        Args:
            file (RemoteFile): The file to download, containing its Google Drive ID.
            local_directory (str): The local directory to save the file.
            logger (logging.Logger): Logger for debugging and information.

        Returns:
            Dict[str, str | int]: Contains the local file path and file size in bytes.
        """
        try:
            file_size = self.file_size(file)
            # I'm putting this check here so we can remove the safety wheels per connector when ready.
            if file_size > self.FILE_SIZE_LIMIT:
                message = "File size exceeds the 1 GB limit."
                raise FileSizeLimitError(message=message, internal_message=message, failure_type=FailureType.config_error)

            file_relative_path, local_file_path, absolute_file_path = self._get_file_transfer_paths(file, local_directory)

            if file.original_mime_type.startswith("application/vnd.google-apps."):
                request = self.google_drive_service.files().export_media(fileId=file.id, mimeType=file.mime_type)
                file_extension = DOWNLOADABLE_DOCUMENTS_MIME_TYPES[file.original_mime_type][DOCUMENT_FILE_EXTENSION_KEY]
                local_file_path += file_extension
                absolute_file_path += file_extension
                file_relative_path += file_extension
            else:
                request = self.google_drive_service.files().get_media(fileId=file.id)

            with open(local_file_path, "wb") as local_file:
                downloader = MediaIoBaseDownload(local_file, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk(num_retries=3)
                    logger.info(f"Processing file {file.uri}, progress: {status}%")

            return {"file_url": absolute_file_path, "bytes": file_size, "file_relative_path": file_relative_path}

        except Exception as e:
            logger.error(f"Failed to download file {file.uri}: {e}")
            raise
