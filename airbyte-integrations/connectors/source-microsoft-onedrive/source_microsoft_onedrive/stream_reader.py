#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import fnmatch
import logging
from contextlib import contextmanager
from functools import lru_cache
from io import IOBase
from typing import Iterable, List, Optional

import smart_open
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from msal import ConfidentialClientApplication
from msal.exceptions import MsalServiceError
from office365.graph_client import GraphClient
from source_microsoft_onedrive.spec import SourceMicrosoftOnedriveSpec


class SourceMicrosoftOneDriveStreamReader(AbstractFileBasedStreamReader):
    """
    A stream reader for Microsoft OneDrive. Handles file enumeration and reading from OneDrive.
    """

    def __init__(self):
        super().__init__()
        self._client = None
        self._config = None

    @property
    def config(self) -> SourceMicrosoftOnedriveSpec:
        """Configuration for Microsoft OneDrive access."""
        return self._config

    @config.setter
    def config(self, value: SourceMicrosoftOnedriveSpec):
        assert isinstance(value, SourceMicrosoftOnedriveSpec), "Config must be an instance of SourceMicrosoftOnedriveSpec."
        self._config = value

    @property
    @lru_cache(maxsize=None)
    def msal_app(self):
        """Returns an MSAL app instance for authentication."""
        return ConfidentialClientApplication(
            self._config.credentials.client_id,
            authority=f"https://login.microsoftonline.com/{self._config.credentials.tenant_id}",
            client_credential=self._config.credentials.client_secret,
        )

    @property
    def client(self):
        """Initializes and returns a GraphClient instance."""
        if self._config is None:
            raise ValueError("Configuration is missing; cannot create the Office365 graph client.")
        if self._client is None:
            self._client = GraphClient(self._get_access_token)
        return self._client

    def _get_access_token(self):
        """Retrieves an access token for OneDrive access."""
        scope = ["https://graph.microsoft.com/.default"]
        refresh_token = self._config.credentials.refresh_token

        if refresh_token:
            result = self.msal_app.acquire_token_by_refresh_token(refresh_token, scopes=scope)
        else:
            result = self.msal_app.acquire_token_for_client(scopes=scope)

        if "access_token" not in result:
            raise MsalServiceError(error=result.get("error"), error_description=result.get("error_description"))

        return result["access_token"]

    def enum_folders_and_files(self, root_folder):
        """Enumerates folders and files starting from a root folder."""
        drive_items = root_folder.children.get().execute_query()
        found_items = [item for item in drive_items if item.is_file or self.enum_folders_and_files(item)]
        return found_items

    def get_files(self, drives):
        """Yields files from the specified drives."""
        for drive in drives:
            yield from self.enum_folders_and_files(drive.root)

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Retrieve all files matching the specified glob patterns in OneDrive.
        """
        my_drive = self.client.me.drive.get().execute_query()
        drives = self.client.drives.get().execute_query()
        drives.add_child(my_drive)

        files = self.get_files(drives)

        # TODO: Fix File downloading logic
        return (file for file in files if any(fnmatch.fnmatch(file.name, glob) for glob in globs))

    @contextmanager
    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        """
        Context manager to open and yield a remote file from OneDrive for reading.
        """
        try:
            with smart_open.open(file.uri, mode=mode.value, encoding=encoding) as file_handle:
                yield file_handle
        except Exception as e:
            logger.exception(f"Error opening file {file.uri}: {e}")
