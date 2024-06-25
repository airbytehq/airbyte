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
        self._auth_client = None
        self._one_drive_client = None

    @property
    def config(self) -> SourceMicrosoftOneDriveSpec:
        return self._config

    @property
    def auth_client(self):
        # Lazy initialization of the auth_client
        if self._auth_client is None:
            self._auth_client = SourceMicrosoftOneDriveClient(self._config)
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
    def config(self, value: SourceMicrosoftOneDriveSpec):
        """
        The FileBasedSource reads and parses configuration from a file, then sets this configuration in its StreamReader. While it only
        uses keys from its abstract configuration, concrete StreamReader implementations may need additional keys for third-party
        authentication. Therefore, subclasses of AbstractFileBasedStreamReader should verify that the value in their config setter
        matches the expected config type for their StreamReader.
        """
        assert isinstance(value, SourceMicrosoftOneDriveSpec)
        self._config = value

    @property
    @lru_cache(maxsize=None)
    def drives(self):
        """
        Retrieves and caches OneDrive drives, including the user's drive based on authentication type.
        """
        drives = self.one_drive_client.drives.get().execute_query()

        if self.config.credentials.auth_type == "Client":
            my_drive = self.one_drive_client.me.drive.get().execute_query()
        else:
            my_drive = (
                self.one_drive_client.users.get_by_principal_name(self.config.credentials.user_principal_name).drive.get().execute_query()
            )

        drives.add_child(my_drive)

        # filter only onedrive drives
        drives = list(filter(lambda drive: drive.drive_type in ["personal", "business"], drives))

        return drives

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

    def list_directories_and_files(self, root_folder, path=None):
        """Enumerates folders and files starting from a root folder."""
        drive_items = root_folder.children.get().execute_query()
        found_items = []
        for item in drive_items:
            item_path = path + "/" + item.name if path else item.name
            if item.is_file:
                found_items.append((item_path, item.properties["@microsoft.graph.downloadUrl"], item.properties["lastModifiedDateTime"]))
            else:
                found_items.extend(self.list_directories_and_files(item, item_path))
        return found_items

    def get_files_by_drive_name(self, drive_name, folder_path):
        """Yields files from the specified drive."""
        path_levels = [level for level in folder_path.split("/") if level]
        folder_path = "/".join(path_levels)

        for drive in self.drives:
            if drive.name == drive_name:
                folder = drive.root if folder_path in self.ROOT_PATH else drive.root.get_by_path(folder_path).get().execute_query()
                yield from self.list_directories_and_files(folder)

    def _get_shared_files_from_all_drives(self, parsed_drive_id: str):
        shared_drive_items = self.one_drive_client.me.drive.shared_with_me().execute_query()
        for drive_item in shared_drive_items:
            parent_reference = drive_item.remote_item.parentReference

            # check if drive is already parsed
            if parent_reference and parent_reference["driveId"] != parsed_drive_id:
                yield from self._get_shared_drive_object(parent_reference["driveId"], drive_item.id, drive_item.web_url)

    def get_all_files(self):
        if self.config.search_scope in ("ACCESSIBLE_DRIVES", "ALL"):
            # Get files from accessible drives
            yield from self.get_files_by_drive_name(self.config.drive_name, self.config.folder_path)

        if self.config.search_scope in ("SHARED_ITEMS", "ALL"):
            selected_drive = list(filter(lambda drive: drive.name == self.config.drive_name, self.drives))
            selected_drive_id = selected_drive[0].id if selected_drive else None

            if self.config.search_scope == "SHARED_ITEMS":
                selected_drive_id = None

            # Get files from shared items
            yield from self._get_shared_files_from_all_drives(selected_drive_id)

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Retrieve all files matching the specified glob patterns in OneDrive.
        """
        files = self.get_all_files()

        try:
            path, download_url, last_modified = next(files)

            yield from self.filter_files_by_globs_and_start_date(
                [
                    MicrosoftOneDriveRemoteFile(
                        uri=path,
                        download_url=download_url,
                        last_modified=last_modified,
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
                    download_url=download_url,
                    last_modified=last_modified,
                )
                for path, download_url, last_modified in files
            ],
            globs,
        )

    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        try:
            return smart_open.open(file.download_url, mode=mode.value, encoding=encoding)
        except Exception as e:
            logger.exception(f"Error opening file {file.uri}: {e}")
