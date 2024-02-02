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
from source_microsoft_sharepoint.spec import SourceMicrosoftSharePointSpec

from .utils import MicrosoftSharePointRemoteFile, execute_query_with_retry, filter_http_urls


class SourceMicrosoftSharePointClient:
    """
    Client to interact with Microsoft SharePoint.
    """

    def __init__(self, config: SourceMicrosoftSharePointSpec):
        self.config = config
        self._client = None
        self._msal_app = ConfidentialClientApplication(
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
        """Retrieves an access token for SharePoint access."""
        scope = ["https://graph.microsoft.com/.default"]
        refresh_token = self.config.credentials.refresh_token if hasattr(self.config.credentials, "refresh_token") else None

        if refresh_token:
            result = self._msal_app.acquire_token_by_refresh_token(refresh_token, scopes=scope)
        else:
            result = self._msal_app.acquire_token_for_client(scopes=scope)

        if "access_token" not in result:
            error_description = result.get("error_description", "No error description provided.")
            message = f"Failed to acquire access token. Error: {result.get('error')}. Error description: {error_description}."
            raise AirbyteTracedException(message=message, failure_type=FailureType.config_error)

        return result


class SourceMicrosoftSharePointStreamReader(AbstractFileBasedStreamReader):
    """
    A stream reader for Microsoft SharePoint. Handles file enumeration and reading from SharePoint.
    """

    ROOT_PATH = [".", "/"]

    def __init__(self):
        super().__init__()
        self._one_drive_client = None

    @property
    def config(self) -> SourceMicrosoftSharePointSpec:
        return self._config

    @property
    def one_drive_client(self) -> SourceMicrosoftSharePointSpec:
        if self._one_drive_client is None:
            self._one_drive_client = SourceMicrosoftSharePointClient(self._config).client
        return self._one_drive_client

    @config.setter
    def config(self, value: SourceMicrosoftSharePointSpec):
        """
        The FileBasedSource reads and parses configuration from a file, then sets this configuration in its StreamReader. While it only
        uses keys from its abstract configuration, concrete StreamReader implementations may need additional keys for third-party
        authentication. Therefore, subclasses of AbstractFileBasedStreamReader should verify that the value in their config setter
        matches the expected config type for their StreamReader.
        """
        assert isinstance(value, SourceMicrosoftSharePointSpec)
        self._config = value

    def _list_directories_and_files(self, root_folder, path=None):
        """Enumerates folders and files starting from a root folder."""
        drive_items = execute_query_with_retry(root_folder.children.get())
        found_items = []
        for item in drive_items:
            item_path = path + "/" + item.name if path else item.name
            if item.is_file:
                found_items.append((item, item_path))
            else:
                found_items.extend(self._list_directories_and_files(item, item_path))
        return found_items

    def _get_files_by_drive_name(self, drives, folder_path):
        """Yields files from the specified drive."""
        path_levels = [level for level in folder_path.split("/") if level]
        folder_path = "/".join(path_levels)

        for drive in drives:
            is_sharepoint = drive.drive_type == "documentLibrary"
            if is_sharepoint:
                folder = (
                    drive.root if folder_path in self.ROOT_PATH else execute_query_with_retry(drive.root.get_by_path(folder_path).get())
                )
                yield from self._list_directories_and_files(folder)

    @property
    @lru_cache(maxsize=None)
    def drives(self):
        """
        Retrieves and caches SharePoint drives, including the user's drive based on authentication type.
        """
        drives = execute_query_with_retry(self.one_drive_client.drives.get())

        if self.config.credentials.auth_type == "Client":
            my_drive = execute_query_with_retry(self.one_drive_client.me.drive.get())
        else:
            my_drive = execute_query_with_retry(
                self.one_drive_client.users.get_by_principal_name(self.config.credentials.user_principal_name).drive.get()
            )

        drives.add_child(my_drive)

        return drives

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Retrieve all files matching the specified glob patterns in SharePoint.
        """
        files = self._get_files_by_drive_name(self.drives, self.config.folder_path)

        files_generator = filter_http_urls(
            self.filter_files_by_globs_and_start_date(
                [
                    MicrosoftSharePointRemoteFile(
                        uri=path,
                        download_url=file.properties["@microsoft.graph.downloadUrl"],
                        last_modified=file.properties["lastModifiedDateTime"],
                    )
                    for file, path in files
                ],
                globs,
            ),
            logger,
        )

        items_processed = False
        for file in files_generator:
            items_processed = True
            yield file

        if not items_processed:
            raise AirbyteTracedException(
                message=f"Drive is empty or does not exist.",
                failure_type=FailureType.config_error,
            )

    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        # choose correct compression mode because the url is random and doesn't end with filename extension
        file_extension = file.uri.split(".")[-1]
        if file_extension in ["gz", "bz2"]:
            compression = "." + file_extension
        else:
            compression = "disable"

        try:
            return smart_open.open(file.download_url, mode=mode.value, compression=compression, encoding=encoding)
        except Exception as e:
            logger.exception(f"Error opening file {file.uri}: {e}")
