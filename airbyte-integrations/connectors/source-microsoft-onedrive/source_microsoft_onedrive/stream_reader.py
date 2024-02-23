#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from functools import lru_cache
from io import IOBase
from typing import Iterable, List, Optional

import smart_open
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType
from msal import ConfidentialClientApplication
from msal.exceptions import MsalServiceError
from office365.graph_client import GraphClient
from source_microsoft_onedrive.spec import SourceMicrosoftOneDriveSpec


class MicrosoftOneDriveRemoteFile(RemoteFile):
    download_url: str


class SourceMicrosoftOneDriveClient:
    """
    Client to interact with Microsoft OneDrive.
    """

    def __init__(self, config: SourceMicrosoftOneDriveSpec):
        self.config = config
        self._client = None

    @property
    @lru_cache(maxsize=None)
    def msal_app(self):
        """Returns an MSAL app instance for authentication."""
        return ConfidentialClientApplication(
            self.config.credentials.client_id,
            authority=f"https://login.microsoftonline.com/{self.config.credentials.tenant_id}",
            client_credential=self.config.credentials.client_secret,
        )

    @property
    def client(self):
        """Initializes and returns a GraphClient instance."""
        if not self.config:
            raise ValueError("Configuration is missing; cannot create the Office365 graph client.")
        if not self._client:
            self._client = GraphClient(self._get_access_token)
        return self._client

    def _get_access_token(self):
        """Retrieves an access token for OneDrive access."""
        scope = ["https://graph.microsoft.com/.default"]
        refresh_token = self.config.credentials.refresh_token if hasattr(self.config.credentials, "refresh_token") else None

        if refresh_token:
            result = self.msal_app.acquire_token_by_refresh_token(refresh_token, scopes=scope)
        else:
            result = self.msal_app.acquire_token_for_client(scopes=scope)

        if "access_token" not in result:
            error_description = result.get("error_description", "No error description provided.")
            raise MsalServiceError(error=result.get("error"), error_description=error_description)

        return result


class SourceMicrosoftOneDriveStreamReader(AbstractFileBasedStreamReader):
    """
    A stream reader for Microsoft OneDrive. Handles file enumeration and reading from OneDrive.
    """

    ROOT_PATH = [".", "/"]

    def __init__(self):
        super().__init__()

    @property
    def config(self) -> SourceMicrosoftOneDriveSpec:
        return self._config

    @property
    def one_drive_client(self) -> SourceMicrosoftOneDriveSpec:
        return SourceMicrosoftOneDriveClient(self._config).client

    @config.setter
    def config(self, value: SourceMicrosoftOneDriveSpec):
        """
        The FileBasedSource reads and parses configuration from a file, then sets this configuration in its StreamReader. While it only
        uses keys from its abstract configuration, concrete StreamReader implementations may need additional keys for third-party
        authentication. Therefore, subclasses of AbstractFileBasedStreamReader should verify that the value in their config setter
        matches the expected config type for their StreamReader.
        """
        assert isinstance(value, SourceMicrosoftOneDriveSpec)
        self._config = value

    def list_directories_and_files(self, root_folder, path=None):
        """Enumerates folders and files starting from a root folder."""
        drive_items = root_folder.children.get().execute_query()
        found_items = []
        for item in drive_items:
            item_path = path + "/" + item.name if path else item.name
            if item.is_file:
                found_items.append((item, item_path))
            else:
                found_items.extend(self.list_directories_and_files(item, item_path))
        return found_items

    def get_files_by_drive_name(self, drives, drive_name, folder_path):
        """Yields files from the specified drive."""
        path_levels = [level for level in folder_path.split("/") if level]
        folder_path = "/".join(path_levels)

        for drive in drives:
            is_onedrive = drive.drive_type in ["personal", "business"]
            if drive.name == drive_name and is_onedrive:
                folder = drive.root if folder_path in self.ROOT_PATH else drive.root.get_by_path(folder_path).get().execute_query()
                yield from self.list_directories_and_files(folder)

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Retrieve all files matching the specified glob patterns in OneDrive.
        """
        drives = self.one_drive_client.drives.get().execute_query()

        if self.config.credentials.auth_type == "Client":
            my_drive = self.one_drive_client.me.drive.get().execute_query()
        else:
            my_drive = (
                self.one_drive_client.users.get_by_principal_name(self.config.credentials.user_principal_name).drive.get().execute_query()
            )

        drives.add_child(my_drive)

        files = self.get_files_by_drive_name(drives, self.config.drive_name, self.config.folder_path)

        try:
            first_file, path = next(files)

            yield from self.filter_files_by_globs_and_start_date(
                [
                    MicrosoftOneDriveRemoteFile(
                        uri=path,
                        download_url=first_file.properties["@microsoft.graph.downloadUrl"],
                        last_modified=first_file.properties["lastModifiedDateTime"],
                    )
                ],
                globs,
            )

        except StopIteration as e:
            raise AirbyteTracedException(
                internal_message=str(e),
                message=f"Drive '{self.config.drive_name}' is empty or does not exist.",
                failure_type=FailureType.config_error,
                exception=e,
            )

        yield from self.filter_files_by_globs_and_start_date(
            [
                MicrosoftOneDriveRemoteFile(
                    uri=path,
                    download_url=file.properties["@microsoft.graph.downloadUrl"],
                    last_modified=file.properties["lastModifiedDateTime"],
                )
                for file, path in files
            ],
            globs,
        )

    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        try:
            return smart_open.open(file.download_url, mode=mode.value, encoding=encoding)
        except Exception as e:
            logger.exception(f"Error opening file {file.uri}: {e}")
