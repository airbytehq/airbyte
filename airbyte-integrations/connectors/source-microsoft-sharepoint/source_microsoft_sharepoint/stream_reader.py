#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from datetime import datetime
from functools import lru_cache
from io import IOBase
from typing import Iterable, List, Optional, Tuple

import requests
import smart_open
from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from msal import ConfidentialClientApplication
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
        self._auth_client = None
        self._one_drive_client = None

    @property
    def config(self) -> SourceMicrosoftSharePointSpec:
        return self._config

    @property
    def auth_client(self):
        # Lazy initialization of the auth_client
        if self._auth_client is None:
            self._auth_client = SourceMicrosoftSharePointClient(self._config)
        return self._auth_client

    @property
    def one_drive_client(self):
        # Lazy initialization of the one_drive_client
        if self._one_drive_client is None:
            self._one_drive_client = self.auth_client.client
        return self._one_drive_client

    def get_access_token(self):
        # Directly fetch a new access token from the auth_client each time it's called
        return self.auth_client._get_access_token()["access_token"]

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

    def _get_shared_drive_object(self, drive_id: str, object_id: str, path: str) -> List[Tuple[str, str, datetime]]:
        """
        Retrieves a list of all nested files under the specified object.

        Args:
            drive_id: The ID of the drive containing the object.
            object_id: The ID of the object to start the search from.

        Returns:
            A list of tuples containing file information (name, download URL, and last modified datetime).

        Raises:
            RuntimeError: If an error occurs during the request.
        """

        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        base_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}"

        def get_files(url: str, path: str) -> List[Tuple[str, str, datetime]]:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                error_info = response.json().get("error", {}).get("message", "No additional error information provided.")
                raise RuntimeError(f"Failed to retrieve files from URL '{url}'. HTTP status: {response.status_code}. Error: {error_info}")

            data = response.json()
            for child in data.get("value", []):
                new_path = path + "/" + child["name"]
                if child.get("file"):  # Object is a file
                    last_modified = datetime.strptime(child["lastModifiedDateTime"], "%Y-%m-%dT%H:%M:%SZ")
                    yield (new_path, child["@microsoft.graph.downloadUrl"], last_modified)
                else:  # Object is a folder, retrieve children
                    child_url = f"{base_url}/items/{child['id']}/children"  # Use item endpoint for nested objects
                    yield from get_files(child_url, new_path)
            yield from []

        # Initial request to item endpoint
        item_url = f"{base_url}/items/{object_id}"
        item_response = requests.get(item_url, headers=headers)
        if item_response.status_code != 200:
            error_info = item_response.json().get("error", {}).get("message", "No additional error information provided.")
            raise RuntimeError(
                f"Failed to retrieve the initial shared object with ID '{object_id}' from drive '{drive_id}'. "
                f"HTTP status: {item_response.status_code}. Error: {error_info}"
            )

        # Check if the object is a file or a folder
        item_data = item_response.json()
        if item_data.get("file"):  # Initial object is a file
            new_path = path + "/" + item_data["name"]
            last_modified = datetime.strptime(item_data["lastModifiedDateTime"], "%Y-%m-%dT%H:%M:%SZ")
            yield (new_path, item_data["@microsoft.graph.downloadUrl"], last_modified)
        else:
            # Initial object is a folder, start file retrieval
            yield from get_files(f"{item_url}/children", path)

    def _list_directories_and_files(self, root_folder, path):
        """Enumerates folders and files starting from a root folder."""
        drive_items = execute_query_with_retry(root_folder.children.get())
        for item in drive_items:
            item_path = path + "/" + item.name if path else item.name
            if item.is_file:
                yield (item_path, item.properties["@microsoft.graph.downloadUrl"], item.properties["lastModifiedDateTime"])
            else:
                yield from self._list_directories_and_files(item, item_path)
        yield from []

    def _get_files_by_drive_name(self, drives, folder_path):
        """Yields files from the specified drive."""
        path_levels = [level for level in folder_path.split("/") if level]
        folder_path = "/".join(path_levels)

        for drive in drives:
            is_sharepoint = drive.drive_type == "documentLibrary"
            if is_sharepoint:
                # Define base path for drive files to differentiate files between drives
                if folder_path in self.ROOT_PATH:
                    folder = drive.root
                    folder_path_url = drive.web_url
                else:
                    folder = execute_query_with_retry(drive.root.get_by_path(folder_path).get())
                    folder_path_url = drive.web_url + "/" + folder_path

                yield from self._list_directories_and_files(folder, folder_path_url)

    @property
    @lru_cache(maxsize=None)
    def drives(self):
        """
        Retrieves and caches SharePoint drives, including the user's drive based on authentication type.
        """
        drives = execute_query_with_retry(self.one_drive_client.drives.get())

        # skip this step for application authentication flow
        if self.config.credentials.auth_type != "Client" or (
            hasattr(self.config.credentials, "refresh_token") and self.config.credentials.refresh_token
        ):
            if self.config.credentials.auth_type == "Client":
                my_drive = execute_query_with_retry(self.one_drive_client.me.drive.get())
            else:
                my_drive = execute_query_with_retry(
                    self.one_drive_client.users.get_by_principal_name(self.config.credentials.user_principal_name).drive.get()
                )

            drives.add_child(my_drive)

        return drives

    def _get_shared_files_from_all_drives(self, parsed_drives):
        drive_ids = [drive.id for drive in parsed_drives]

        shared_drive_items = execute_query_with_retry(self.one_drive_client.me.drive.shared_with_me())
        for drive_item in shared_drive_items:
            parent_reference = drive_item.remote_item.parentReference

            # check if drive is already parsed
            if parent_reference and parent_reference["driveId"] not in drive_ids:
                yield from self._get_shared_drive_object(parent_reference["driveId"], drive_item.id, drive_item.web_url)

    def get_all_files(self):
        if self.config.search_scope in ("ACCESSIBLE_DRIVES", "ALL"):
            # Get files from accessible drives
            yield from self._get_files_by_drive_name(self.drives, self.config.folder_path)

        # skip this step for application authentication flow
        if self.config.credentials.auth_type != "Client" or (
            hasattr(self.config.credentials, "refresh_token") and self.config.credentials.refresh_token
        ):
            if self.config.search_scope in ("SHARED_ITEMS", "ALL"):
                parsed_drives = [] if self.config.search_scope == "SHARED_ITEMS" else self.drives

                # Get files from shared items
                yield from self._get_shared_files_from_all_drives(parsed_drives)

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Retrieve all files matching the specified glob patterns in SharePoint.
        """
        files = self.get_all_files()

        files_generator = filter_http_urls(
            self.filter_files_by_globs_and_start_date(
                [
                    MicrosoftSharePointRemoteFile(
                        uri=path,
                        download_url=download_url,
                        last_modified=last_modified,
                    )
                    for path, download_url, last_modified in files
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
