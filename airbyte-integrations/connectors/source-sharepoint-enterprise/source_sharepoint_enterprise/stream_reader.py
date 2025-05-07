#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import re
from datetime import datetime
from functools import lru_cache
from io import IOBase
from os import makedirs, path
from os.path import getsize
from typing import Any, Dict, Iterable, List, MutableMapping, Optional, Tuple

import requests
import smart_open
from office365.entity_collection import EntityCollection
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.drives.drive import Drive
from office365.sharepoint.search.service import SearchService

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.models import AirbyteRecordMessageFileReference
from airbyte_cdk.sources.file_based.exceptions import FileSizeLimitError
from airbyte_cdk.sources.file_based.file_based_stream_reader import (
    AbstractFileBasedStreamReader,
    FileReadMode,
)
from airbyte_cdk.sources.file_based.file_record_data import FileRecordData
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from source_sharepoint_enterprise.sharepoint_base_reader import SharepointBaseReader

from .exceptions import ErrorFetchingMetadata
from .utils import (
    FolderNotFoundException,
    MicrosoftSharePointRemoteFile,
    execute_query_with_retry,
    filter_http_urls,
)


SITE_TITLE = "Title"
SITE_PATH = "Path"


class SourceMicrosoftSharePointStreamReader(SharepointBaseReader, AbstractFileBasedStreamReader):
    """
    A stream reader for Microsoft SharePoint. Handles file enumeration and reading from SharePoint.
    """

    ROOT_PATH = [".", "/"]
    FILE_SIZE_LIMIT = 1_500_000_000

    def __init__(self):
        AbstractFileBasedStreamReader.__init__(self)
        SharepointBaseReader.__init__(self)

    def get_access_token(self):
        # Directly fetch a new access token from the auth_client each time it's called
        return self.auth_client.access_token

    def _get_shared_drive_object(self, drive_id: str, object_id: str, path: str) -> Iterable[MicrosoftSharePointRemoteFile]:
        """
        Retrieves a list of all nested files under the specified object.

        Args:
            drive_id: The ID of the drive containing the object.
            object_id: The ID of the object to start the search from.

        Returns:
            An iterable of MicrosoftSharePointRemoteFile instances containing file information.

        Raises:
            RuntimeError: If an error occurs during the request.
        """

        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        base_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}"

        def get_files(url: str, path: str) -> Iterable[MicrosoftSharePointRemoteFile]:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                error_info = response.json().get("error", {}).get("message", "No additional error information provided.")
                raise RuntimeError(f"Failed to retrieve files from URL '{url}'. HTTP status: {response.status_code}. Error: {error_info}")

            data = response.json()
            for child in data.get("value", []):
                new_path = path + "/" + child["name"]
                if child.get("file"):  # Object is a file
                    # last_modified and created_at are type string e.g. "2025-04-16T14:41:00Z"
                    last_modified = datetime.strptime(child["lastModifiedDateTime"], "%Y-%m-%dT%H:%M:%SZ")
                    created_at = datetime.strptime(child["createdDateTime"], "%Y-%m-%dT%H:%M:%SZ")
                    yield MicrosoftSharePointRemoteFile(
                        uri=new_path,
                        download_url=child["@microsoft.graph.downloadUrl"],
                        last_modified=last_modified,
                        created_at=created_at,
                        id=child.get("id"),
                        drive_id=drive_id,
                        from_shared_drive=True,
                    )
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
            created_at = datetime.strptime(item_data["createdDateTime"], "%Y-%m-%dT%H:%M:%SZ")
            yield MicrosoftSharePointRemoteFile(
                uri=new_path,
                download_url=item_data["@microsoft.graph.downloadUrl"],
                last_modified=last_modified,
                created_at=created_at,
                id=item_data.get("id"),
                drive_id=drive_id,
                from_shared_drive=True,
            )
        else:
            # Initial object is a folder, start file retrieval
            yield from get_files(f"{item_url}/children", path)

    def _list_directories_and_files(self, root_folder: DriveItem, path: str, drive_id: str) -> Iterable[MicrosoftSharePointRemoteFile]:
        """Enumerates folders and files starting from a root folder.""" """
        Enumerates folders and files starting from a root folder.
    
        Args:
            root_folder (DriveItem): The root folder to start the enumeration from.
            path (str): The current path in the directory structure.
    
        Yields:
            Tuple[str, str, str, str]: A tuple containing the file path, download URL, last modified date, and file ID.
        """
        drive_items = execute_query_with_retry(root_folder.children.get())
        for item in drive_items:
            item_path = path + "/" + item.name if path else item.name
            if item.is_file:
                # last_modified and created_at are type datetime.datetime e.g. (2025, 2, 18, 19, 32, 4)
                yield MicrosoftSharePointRemoteFile(
                    uri=item_path,
                    download_url=item.properties["@microsoft.graph.downloadUrl"],
                    last_modified=item.properties["lastModifiedDateTime"],
                    created_at=item.properties["createdDateTime"],
                    id=item.id,
                    drive_id=drive_id,
                    from_shared_drive=False,
                )
            else:
                yield from self._list_directories_and_files(item, item_path, drive_id)
        yield from []

    def _get_files_by_drive_name(self, drives, folder_path) -> Iterable[MicrosoftSharePointRemoteFile]:
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
                    try:
                        folder = execute_query_with_retry(drive.root.get_by_path(folder_path).get())
                    except FolderNotFoundException:
                        continue
                    folder_path_url = drive.web_url + "/" + folder_path

                yield from self._list_directories_and_files(folder, folder_path_url, drive_id=drive.id)

    def get_all_sites(self) -> List[MutableMapping[str, Any]]:
        """
        Retrieves all SharePoint sites from the current tenant.

        Returns:
            List[MutableMapping[str, Any]]: A list of site information.
        """
        ctx = self._get_client_context()
        search_service = SearchService(ctx)
        # ignore default OneDrive site with NOT Path:https://prefix-my.sharepoint.com
        search_job = search_service.post_query(f"contentclass:STS_Site NOT Path:https://{self.root_site_prefix}-my.sharepoint.com")
        search_job_result = execute_query_with_retry(search_job)

        found_sites = []
        if search_job.value and search_job_result.value.PrimaryQueryResult:
            table = search_job_result.value.PrimaryQueryResult.RelevantResults.Table
            for row in table.Rows:
                found_site = {}
                data = row.Cells
                found_site[SITE_TITLE] = data.get(SITE_TITLE)
                found_site[SITE_PATH] = data.get(SITE_PATH)
                found_sites.append(found_site)
        else:
            raise Exception("No site collections found")

        return found_sites

    def _get_drives_from_sites(self, sites: List[MutableMapping[str, Any]]) -> EntityCollection:
        """
        Retrieves SharePoint drives from the provided sites.
        Args:
            sites (List[MutableMapping[str, Any]]): A list of site information.

        Returns:
            EntityCollection: A collection of SharePoint drives.
        """
        all_sites_drives = EntityCollection(context=self.one_drive_client, item_type=Drive)
        for site in sites:
            drives = execute_query_with_retry(self.one_drive_client.sites.get_by_url(site[SITE_PATH]).drives.get())
            for site_drive in drives:
                all_sites_drives.add_child(site_drive)
        return all_sites_drives

    def _get_site_drive(self) -> EntityCollection:
        """
        Retrieves SharePoint drives based on the provided site URL.
        It iterates over the sites if something like sharepoint.com/sites/ is in the site_url.
        Returns:
            EntityCollection: A collection of SharePoint drives.

        Raises:
            AirbyteTracedException: If an error occurs while retrieving drives.
        """
        try:
            if not self.config.site_url:
                # get main site drives
                drives = execute_query_with_retry(self.one_drive_client.drives.get())
            elif re.search(r"sharepoint\.com/sites/?$", self.config.site_url):
                # get all sites and then get drives from each site
                return self._get_drives_from_sites(self.get_all_sites())
            else:
                # get drives for site drives provided in the config
                drives = execute_query_with_retry(self.one_drive_client.sites.get_by_url(self.config.site_url).drives.get())

            return drives
        except Exception as ex:
            site = self.config.site_url if self.config.site_url else "default"
            raise AirbyteTracedException(
                f"Failed to retrieve drives from sharepoint {site} site. Error: {str(ex)}",
                failure_type=FailureType.config_error,
            )

    @property
    @lru_cache(maxsize=None)
    def drives(self) -> EntityCollection:
        """
        Retrieves and caches SharePoint drives, including the user's drive based on authentication type.
        """
        drives = self._get_site_drive()

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

    def _get_shared_files_from_all_drives(self, parsed_drives) -> Iterable[MicrosoftSharePointRemoteFile]:
        drive_ids = [drive.id for drive in parsed_drives]

        shared_drive_items = execute_query_with_retry(self.one_drive_client.me.drive.shared_with_me())
        for drive_item in shared_drive_items:
            parent_reference = drive_item.remote_item.parentReference

            # check if drive is already parsed
            if parent_reference and parent_reference["driveId"] not in drive_ids:
                yield from self._get_shared_drive_object(parent_reference["driveId"], drive_item.id, drive_item.web_url)

    def get_all_files(self) -> Iterable[MicrosoftSharePointRemoteFile]:
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
            self.filter_files_by_globs_and_start_date([file for file in files], globs),
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

    def open_file(
        self,
        file: RemoteFile,
        mode: FileReadMode,
        encoding: Optional[str],
        logger: logging.Logger,
    ) -> IOBase:
        # choose correct compression mode because the url is random and doesn't end with filename extension
        file_extension = file.uri.split(".")[-1]
        if file_extension in ["gz", "bz2"]:
            compression = "." + file_extension
        else:
            compression = "disable"

        try:
            return smart_open.open(
                file.download_url,
                mode=mode.value,
                compression=compression,
                encoding=encoding,
            )
        except Exception as e:
            logger.exception(f"Error opening file {file.uri}: {e}")

    @staticmethod
    def _parse_file_path_from_uri(file_uri: str) -> str:
        match = re.search(r"sharepoint\.com(?:/sites/[^/]+)?/Shared%20Documents(.*)", file_uri)
        return match.group(1) if match else file_uri

    def _get_headers(self) -> Dict[str, str]:
        access_token = self.get_access_token()
        return {"Authorization": f"Bearer {access_token}"}

    def file_size(self, file: MicrosoftSharePointRemoteFile) -> int:
        """
        Retrieves the size of a file in Microsoft SharePoint.

        Args:
            file (RemoteFile): The file to get the size for.

        Returns:
            int: The file size in bytes.
        """
        try:
            headers = self._get_headers()
            response = requests.head(file.download_url, headers=headers)
            response.raise_for_status()
            return int(response.headers["Content-Length"])
        except KeyError:
            raise ErrorFetchingMetadata(f"Size was expected in metadata response but was missing")
        except Exception as e:
            raise ErrorFetchingMetadata(f"An error occurred while retrieving file size: {str(e)}")

    def upload(
        self, file: MicrosoftSharePointRemoteFile, local_directory: str, logger: logging.Logger
    ) -> Tuple[FileRecordData, AirbyteRecordMessageFileReference]:
        """
        Downloads a file from Microsoft SharePoint to a specified local directory.

        Args:
            file (RemoteFile): The file to download, containing its SharePoint URL.
            local_directory (str): The local directory to save the file.
            logger (logging.Logger): Logger for debugging and information.

        Returns:
            Dict[str, str | int]: Contains the local file path and file size in bytes.
        """
        file_size = self.file_size(file)
        if file_size > self.FILE_SIZE_LIMIT:
            message = "File size exceeds the size limit."
            raise FileSizeLimitError(
                message=message,
                internal_message=message,
                failure_type=FailureType.config_error,
            )

        try:
            file_paths = self._get_file_transfer_paths(
                source_file_relative_path=self._parse_file_path_from_uri(file.uri), staging_directory=local_directory
            )
            local_file_path = file_paths[self.LOCAL_FILE_PATH]
            file_relative_path = file_paths[self.FILE_RELATIVE_PATH]
            file_name = file_paths[self.FILE_NAME]

            headers = self._get_headers()

            # Download the file
            #  By using stream=True, the file content is streamed in chunks, which allows to process each chunk individually.
            #  https://docs.python-requests.org/en/latest/user/quickstart/#raw-response-content
            response = requests.get(file.download_url, headers=headers, stream=True)
            response.raise_for_status()

            # Write the file to the local directory
            with open(local_file_path, "wb") as local_file:
                for chunk in response.iter_content(chunk_size=10_485_760):
                    if chunk:
                        local_file.write(chunk)

            # Get the file size
            file_size = getsize(local_file_path)

            file_record_data = FileRecordData(
                folder=file_paths[self.FILE_FOLDER],
                file_name=file_name,
                bytes=file_size,
                source_uri=file.uri,
                created_at=file.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                updated_at=file.last_modified.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            )

            file_reference = AirbyteRecordMessageFileReference(
                staging_file_url=local_file_path,
                source_file_relative_path=file_relative_path,
                file_size_bytes=file_size,
            )

            return file_record_data, file_reference

        except Exception as e:
            raise AirbyteTracedException(
                f"There was an error while trying to download the file {file.uri}: {str(e)}",
                failure_type=FailureType.config_error,
            )
