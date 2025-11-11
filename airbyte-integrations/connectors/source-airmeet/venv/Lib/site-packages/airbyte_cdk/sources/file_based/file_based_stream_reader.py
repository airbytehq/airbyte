#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from io import IOBase
from os import makedirs, path
from typing import Any, Iterable, List, MutableMapping, Optional, Set, Tuple

from airbyte_protocol_dataclasses.models import FailureType
from wcmatch.glob import GLOBSTAR, globmatch

from airbyte_cdk.models import AirbyteRecordMessageFileReference
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.config.validate_config_transfer_modes import (
    include_identities_stream,
    preserve_directory_structure,
    use_file_transfer,
)
from airbyte_cdk.sources.file_based.exceptions import FileSizeLimitError
from airbyte_cdk.sources.file_based.file_record_data import FileRecordData
from airbyte_cdk.sources.file_based.remote_file import RemoteFile, UploadableRemoteFile


class FileReadMode(Enum):
    READ = "r"
    READ_BINARY = "rb"


class AbstractFileBasedStreamReader(ABC):
    DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    FILE_RELATIVE_PATH = "file_relative_path"
    FILE_NAME = "file_name"
    LOCAL_FILE_PATH = "local_file_path"
    FILE_FOLDER = "file_folder"
    FILE_SIZE_LIMIT = 1_500_000_000

    def __init__(self) -> None:
        self._config = None

    @property
    def config(self) -> Optional[AbstractFileBasedSpec]:
        return self._config

    @config.setter
    @abstractmethod
    def config(self, value: AbstractFileBasedSpec) -> None:
        """
        FileBasedSource reads the config from disk and parses it, and once parsed, the source sets the config on its StreamReader.

        Note: FileBasedSource only requires the keys defined in the abstract config, whereas concrete implementations of StreamReader
        will require keys that (for example) allow it to authenticate with the 3rd party.

        Therefore, concrete implementations of AbstractFileBasedStreamReader's config setter should assert that `value` is of the correct
        config type for that type of StreamReader.
        """
        ...

    @abstractmethod
    def open_file(
        self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger
    ) -> IOBase:
        """
        Return a file handle for reading.

        Many sources will be able to use smart_open to implement this method,
        for example:

        client = boto3.Session(...)
        return smart_open.open(remote_file.uri, transport_params={"client": client})
        """
        ...

    @abstractmethod
    def get_matching_files(
        self,
        globs: List[str],
        prefix: Optional[str],
        logger: logging.Logger,
    ) -> Iterable[RemoteFile]:
        """
        Return all files that match any of the globs.

        Example:

        The source has files "a.json", "foo/a.json", "foo/bar/a.json"

        If globs = ["*.json"] then this method returns ["a.json"].

        If globs = ["foo/*.json"] then this method returns ["foo/a.json"].

        Utility method `self.filter_files_by_globs` and `self.get_prefixes_from_globs`
        are available, which may be helpful when implementing this method.
        """
        ...

    def filter_files_by_globs_and_start_date(
        self, files: List[RemoteFile], globs: List[str]
    ) -> Iterable[RemoteFile]:
        """
        Utility method for filtering files based on globs.
        """
        start_date = (
            datetime.strptime(self.config.start_date, self.DATE_TIME_FORMAT)
            if self.config and self.config.start_date
            else None
        )
        seen = set()

        for file in files:
            if self.file_matches_globs(file, globs):
                if file.uri not in seen and (not start_date or file.last_modified >= start_date):
                    seen.add(file.uri)
                    yield file

    @staticmethod
    def file_matches_globs(file: RemoteFile, globs: List[str]) -> bool:
        # Use the GLOBSTAR flag to enable recursive ** matching
        # (https://facelessuser.github.io/wcmatch/wcmatch/#globstar)
        return any(globmatch(file.uri, g, flags=GLOBSTAR) for g in globs)

    @staticmethod
    def get_prefixes_from_globs(globs: List[str]) -> Set[str]:
        """
        Utility method for extracting prefixes from the globs.
        """
        prefixes = {glob.split("*")[0] for glob in globs}
        return set(filter(lambda x: bool(x), prefixes))

    def use_file_transfer(self) -> bool:
        if self.config:
            return use_file_transfer(self.config)
        return False

    def preserve_directory_structure(self) -> bool:
        # fall back to preserve subdirectories if config is not present or incomplete
        if self.config:
            return preserve_directory_structure(self.config)
        return True

    def include_identities_stream(self) -> bool:
        if self.config:
            return include_identities_stream(self.config)
        return False

    def upload(
        self, file: UploadableRemoteFile, local_directory: str, logger: logging.Logger
    ) -> Tuple[FileRecordData, AirbyteRecordMessageFileReference]:
        """
        This is required for connectors that will support writing to
        files. It will handle the logic to download,get,read,acquire or
        whatever is more efficient to get a file from the source.

        Args:
               file (RemoteFile): The remote file object containing URI and metadata.
               local_directory (str): The local directory path where the file will be downloaded.
               logger (logging.Logger): Logger for logging information and errors.

           Returns:
               AirbyteRecordMessageFileReference: A file reference object containing:
                   - staging_file_url (str): The absolute path to the referenced file in the staging area.
                   - file_size_bytes (int): The size of the referenced file in bytes.
                   - source_file_relative_path (str): The relative path to the referenced file in source.
        """
        if not isinstance(file, UploadableRemoteFile):
            raise TypeError(f"Expected UploadableRemoteFile, got {type(file)}")

        file_size = file.size

        if file_size > self.FILE_SIZE_LIMIT:
            message = f"File size exceeds the {self.FILE_SIZE_LIMIT / 1e9} GB limit."
            raise FileSizeLimitError(
                message=message, internal_message=message, failure_type=FailureType.config_error
            )

        file_paths = self._get_file_transfer_paths(
            source_file_relative_path=file.source_file_relative_path,
            staging_directory=local_directory,
        )
        local_file_path = file_paths[self.LOCAL_FILE_PATH]
        file_relative_path = file_paths[self.FILE_RELATIVE_PATH]
        file_name = file_paths[self.FILE_NAME]

        logger.info(
            f"Starting to download the file {file.file_uri_for_logging} with size: {file_size / (1024 * 1024):,.2f} MB ({file_size / (1024 * 1024 * 1024):.2f} GB)"
        )
        start_download_time = time.time()

        file.download_to_local_directory(local_file_path)

        write_duration = time.time() - start_download_time
        logger.info(
            f"Finished downloading the file {file.file_uri_for_logging} and saved to {local_file_path} in {write_duration:,.2f} seconds."
        )

        file_record_data = FileRecordData(
            folder=file_paths[self.FILE_FOLDER],
            file_name=file_name,
            bytes=file_size,
            id=file.id,
            mime_type=file.mime_type,
            created_at=file.created_at,
            updated_at=file.updated_at,
            source_uri=file.uri,
        )
        file_reference = AirbyteRecordMessageFileReference(
            staging_file_url=local_file_path,
            source_file_relative_path=file_relative_path,
            file_size_bytes=file_size,
        )
        return file_record_data, file_reference

    def _get_file_transfer_paths(
        self, source_file_relative_path: str, staging_directory: str
    ) -> MutableMapping[str, Any]:
        """
        This method is used to get the file transfer paths for a given source file relative path and local directory.
        It returns a dictionary with the following keys:
            - FILE_RELATIVE_PATH: The relative path to file in reference to the staging directory.
            - LOCAL_FILE_PATH: The absolute path to the file.
            - FILE_NAME: The name of the referenced file.
            - FILE_FOLDER: The folder of the referenced file.
        """
        preserve_directory_structure = self.preserve_directory_structure()

        file_name = path.basename(source_file_relative_path)
        file_folder = path.dirname(source_file_relative_path)
        if preserve_directory_structure:
            # Remove left slashes from source path format to make relative path for writing locally
            file_relative_path = source_file_relative_path.lstrip("/")
        else:
            file_relative_path = file_name
        local_file_path = path.join(staging_directory, file_relative_path)
        # Ensure the local directory exists
        makedirs(path.dirname(local_file_path), exist_ok=True)

        file_paths = {
            self.FILE_RELATIVE_PATH: file_relative_path,
            self.LOCAL_FILE_PATH: local_file_path,
            self.FILE_NAME: file_name,
            self.FILE_FOLDER: file_folder,
        }
        return file_paths
