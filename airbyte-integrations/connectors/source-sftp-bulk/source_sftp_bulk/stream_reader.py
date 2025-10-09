# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import datetime
import fnmatch
import logging
import stat
import time
from io import IOBase
from typing import Iterable, List, Optional, Set, Tuple

import psutil
from typing_extensions import override

from airbyte_cdk import FailureType
from airbyte_cdk.models import AirbyteRecordMessageFileReference
from airbyte_cdk.sources.file_based.exceptions import FileSizeLimitError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.file_record_data import FileRecordData
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from source_sftp_bulk.client import SFTPClient
from source_sftp_bulk.spec import SourceSFTPBulkSpec


class SourceSFTPBulkStreamReader(AbstractFileBasedStreamReader):
    FILE_SIZE_LIMIT = 1_500_000_000

    def __init__(self):
        super().__init__()
        self._sftp_client = None

    @property
    def config(self) -> SourceSFTPBulkSpec:
        return self._config

    @config.setter
    def config(self, value: SourceSFTPBulkSpec):
        """
        FileBasedSource reads the config from disk and parses it, and once parsed, the source sets the config on its StreamReader.

        Note: FileBasedSource only requires the keys defined in the abstract config, whereas concrete implementations of StreamReader
        will require keys that (for example) allow it to authenticate with the 3rd party.

        Therefore, concrete implementations of AbstractFileBasedStreamReader's config setter should assert that `value` is of the correct
        config type for that type of StreamReader.
        """
        assert isinstance(value, SourceSFTPBulkSpec)
        self._config = value

    @property
    def sftp_client(self) -> SFTPClient:
        if self._sftp_client is None:
            authentication = (
                {"password": self.config.credentials.password}
                if self.config.credentials.auth_type == "password"
                else {"private_key": self.config.credentials.private_key}
            )
            self._sftp_client = SFTPClient(
                host=self.config.host,
                username=self.config.username,
                **authentication,
                port=self.config.port,
            )
        return self._sftp_client

    def _is_directory_excluded(
        self, directory_path: str, excluded_absolute_paths: Set[str], excluded_patterns: List[str]
    ) -> bool:
        """
        Check if a directory should be excluded based on configured exclusion rules.

        Args:
            directory_path: The full path of the directory to check
            excluded_absolute_paths: Set of exact directory paths to exclude
            excluded_patterns: List of glob patterns to match against

        Returns:
            True if the directory should be excluded, False otherwise
        """
        # Check exact path match (O(1) lookup)
        if directory_path in excluded_absolute_paths:
            return True

        # Check glob patterns
        for pattern in excluded_patterns:
            # Support both Unix-style patterns and full path patterns
            if fnmatch.fnmatch(directory_path, pattern):
                return True
            # Also check if just the directory name matches the pattern
            # This allows patterns like "**/node_modules" to work
            if '**/' in pattern:
                # Extract the part after **/ and match against path segments
                suffix_pattern = pattern.split('**/', 1)[1]
                if fnmatch.fnmatch(directory_path, f"**/{suffix_pattern}") or directory_path.endswith(f"/{suffix_pattern}"):
                    return True

        return False

    def get_matching_files(
        self,
        globs: List[str],
        prefix: Optional[str],
        logger: logging.Logger,
    ) -> Iterable[RemoteFile]:
        root_path = self._config.folder_path or "/"
        directories = [(root_path, 0)]  # (path, depth)
        seen_dirs = set()  # Track visited directories to prevent loops

        # Traversal statistics
        total_dirs_visited = 0
        total_files_found = 0
        total_dirs_excluded = 0
        max_depth_reached = 0

        # Configuration for traversal limits
        max_depth = self._config.max_traversal_depth
        PROGRESS_LOG_INTERVAL = 100  # Log every N directories

        # Parse exclusion patterns
        excluded_absolute_paths: Set[str] = set()
        excluded_patterns: List[str] = []
        for exclusion in self._config.excluded_directories:
            if '*' in exclusion or '?' in exclusion:
                excluded_patterns.append(exclusion)
            else:
                excluded_absolute_paths.add(exclusion)

        # Get prefixes from globs for early pruning (if available from parent class)
        prefixes = self.get_prefixes_from_globs(globs) if globs else []

        logger.info(
            f"Starting file discovery from '{root_path}' with globs: {globs}, "
            f"max depth: {max_depth}, excluded directories: {len(self._config.excluded_directories)}"
        )

        # Iterate through directories and subdirectories
        while directories:
            current_dir, depth = directories.pop()

            # Prevent infinite loops by tracking visited directories
            if current_dir in seen_dirs:
                logger.debug(f"Skipping already visited directory: {current_dir}")
                continue
            seen_dirs.add(current_dir)

            # Enforce depth limit
            if depth > max_depth:
                logger.warning(f"Max depth ({max_depth}) reached at '{current_dir}', skipping deeper traversal")
                continue

            max_depth_reached = max(max_depth_reached, depth)
            total_dirs_visited += 1

            # Progress logging with memory monitoring
            if total_dirs_visited % PROGRESS_LOG_INTERVAL == 0:
                memory_info = psutil.virtual_memory()
                memory_used_mb = (memory_info.total - memory_info.available) / (1024 * 1024)
                memory_percent = memory_info.percent
                logger.info(
                    f"Discovery progress: visited {total_dirs_visited} directories, "
                    f"found {total_files_found} matching files, current depth: {depth}, "
                    f"directories queued: {len(directories)}, "
                    f"memory usage: {memory_used_mb:,.0f} MB ({memory_percent:.1f}%)"
                )

            try:
                items = self.sftp_client.sftp_connection.listdir_attr(current_dir)
                logger.debug(f"Listed {len(items)} items in '{current_dir}'")
            except PermissionError as e:
                logger.warning(f"Permission denied accessing directory '{current_dir}': {e}")
                continue
            except Exception as e:
                logger.warning(f"Failed to list files in directory '{current_dir}': {e}")
                continue

            for item in items:
                # Construct full path (maintain backward-compatible path construction)
                full_path = f"{current_dir}/{item.filename}"

                if item.st_mode and stat.S_ISDIR(item.st_mode):
                    # Check if directory is excluded
                    if self._is_directory_excluded(full_path, excluded_absolute_paths, excluded_patterns):
                        logger.debug(f"Excluding directory '{full_path}' - matches exclusion pattern")
                        total_dirs_excluded += 1
                        continue

                    # Early pruning: check if directory path could match any glob patterns
                    should_traverse = True
                    if prefixes:
                        # Check if this directory could contain files matching our prefixes
                        dir_path_with_slash = full_path + "/"
                        # Only traverse if directory path is a prefix of any glob prefix, or vice versa
                        should_traverse = any(
                            prefix.startswith(dir_path_with_slash) or dir_path_with_slash.startswith(prefix)
                            for prefix in prefixes
                        )

                    if should_traverse:
                        directories.append((full_path, depth + 1))
                    else:
                        logger.debug(f"Skipping directory '{full_path}' - does not match glob prefixes")
                else:
                    # Process file
                    try:
                        remote_file = RemoteFile(
                            uri=full_path,
                            last_modified=datetime.datetime.fromtimestamp(item.st_mtime)
                        )
                        # Use filter_files_by_globs_and_start_date from parent class
                        matching_files = list(self.filter_files_by_globs_and_start_date([remote_file], globs))
                        if matching_files:
                            total_files_found += len(matching_files)
                            yield from matching_files
                    except Exception as e:
                        logger.warning(f"Error processing file '{full_path}': {e}")

        # Final summary
        logger.info(
            f"File discovery completed: visited {total_dirs_visited} directories, "
            f"excluded {total_dirs_excluded} directories, "
            f"found {total_files_found} matching files, max depth: {max_depth_reached}"
        )

    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        remote_file = self.sftp_client.sftp_connection.open(file.uri, mode=mode.value)
        return remote_file

    @staticmethod
    def create_progress_handler(local_file_path: str, logger: logging.Logger):
        previous_bytes_copied = 0

        def progress_handler(bytes_copied, total_bytes):
            nonlocal previous_bytes_copied
            if bytes_copied - previous_bytes_copied >= 100 * 1024 * 1024:
                logger.info(
                    f"{bytes_copied / (1024 * 1024):,.2f} MB ({bytes_copied / (1024 * 1024 * 1024):.2f} GB) "
                    f"of {total_bytes / (1024 * 1024):,.2f} MB ({total_bytes / (1024 * 1024 * 1024):.2f} GB) "
                    f"written to {local_file_path}"
                )
                previous_bytes_copied = bytes_copied

                # Get available disk space
                disk_usage = psutil.disk_usage("/")
                available_disk_space = disk_usage.free

                # Get available memory
                memory_info = psutil.virtual_memory()
                available_memory = memory_info.available
                logger.info(
                    f"Available disk space: {available_disk_space / (1024 * 1024):,.2f} MB ({available_disk_space / (1024 * 1024 * 1024):.2f} GB), "
                    f"available memory: {available_memory / (1024 * 1024):,.2f} MB ({available_memory / (1024 * 1024 * 1024):.2f} GB)."
                )

        return progress_handler

    @override
    def upload(
        self, file: RemoteFile, local_directory: str, logger: logging.Logger
    ) -> Tuple[FileRecordData, AirbyteRecordMessageFileReference]:
        """
        Downloads a file from SFTP server to a specified local directory.

        Args:
            file (RemoteFile): The remote file object containing URI and metadata.
            local_directory (str): The local directory path where the file will be downloaded.
            logger (logging.Logger): Logger for logging information and errors.

        Returns:
            Tuple[FileRecordData, AirbyteRecordMessageFileReference]: Contains file record data and file reference for Airbyte protocol.

        Raises:
            FileSizeLimitError: If the file size exceeds the predefined limit (1 GB).
        """
        file_size = self.file_size(file)
        # I'm putting this check here so we can remove the safety wheels per connector when ready.
        if file_size > self.FILE_SIZE_LIMIT:
            message = "File size exceeds the 1 GB limit."
            raise FileSizeLimitError(message=message, internal_message=message, failure_type=FailureType.config_error)

        file_paths = self._get_file_transfer_paths(file.uri, local_directory)
        local_file_path = file_paths[self.LOCAL_FILE_PATH]
        file_relative_path = file_paths[self.FILE_RELATIVE_PATH]
        file_name = file_paths[self.FILE_NAME]

        # Get available disk space
        disk_usage = psutil.disk_usage("/")
        available_disk_space = disk_usage.free

        # Get available memory
        memory_info = psutil.virtual_memory()
        available_memory = memory_info.available

        # Log file size, available disk space, and memory
        logger.info(
            f"Starting to download the file {file.uri} with size: {file_size / (1024 * 1024):,.2f} MB ({file_size / (1024 * 1024 * 1024):.2f} GB) "
            f"to '{local_file_path}' "
            f"with size: {file_size / (1024 * 1024):,.2f} MB ({file_size / (1024 * 1024 * 1024):.2f} GB), "
            f"available disk space: {available_disk_space / (1024 * 1024):,.2f} MB ({available_disk_space / (1024 * 1024 * 1024):.2f} GB),"
            f"available memory: {available_memory / (1024 * 1024):,.2f} MB ({available_memory / (1024 * 1024 * 1024):.2f} GB)."
        )
        progress_handler = self.create_progress_handler(local_file_path, logger)
        start_download_time = time.time()
        # Copy a remote file in remote path from the SFTP server to the local host as local path.
        self.sftp_client.sftp_connection.get(file.uri, local_file_path, callback=progress_handler)

        download_duration = time.time() - start_download_time
        logger.info(f"Time taken to download the file {file.uri}: {download_duration:,.2f} seconds.")
        logger.info(f"File {file_relative_path} successfully written to {local_directory}.")

        file_record_data = FileRecordData(
            folder=file_paths[self.FILE_FOLDER],
            file_name=file_name,
            bytes=file_size,
            updated_at=file.last_modified.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            source_uri=f"sftp://{self.config.username}@{self.config.host}:{self.config.port}{file.uri}",
        )

        file_reference = AirbyteRecordMessageFileReference(
            staging_file_url=local_file_path,
            source_file_relative_path=file_relative_path,
            file_size_bytes=file_size,
        )

        return file_record_data, file_reference

    def file_size(self, file: RemoteFile):
        file_size = self.sftp_client.sftp_connection.stat(file.uri).st_size
        return file_size
