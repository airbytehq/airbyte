# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import logging
import stat
from datetime import datetime
from io import IOBase
from typing import Any, Iterable, List, Optional

import psutil
from wcmatch.glob import GLOBSTAR, globmatch

from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import UploadableRemoteFile
from source_sftp_bulk.client import SFTPClient
from source_sftp_bulk.spec import SourceSFTPBulkSpec


class SFTPBulkUploadableRemoteFile(UploadableRemoteFile):
    sftp_client: Any
    logger: Any
    config: Any

    def __init__(self, sftp_client: SFTPClient, logger: logging.Logger, **kwargs):
        super().__init__(**kwargs)
        self.sftp_client = sftp_client
        self.logger = logger

    @property
    def size(self) -> int:
        file_size = self.sftp_client.sftp_connection.stat(self.uri).st_size
        return file_size

    @property
    def source_uri(self) -> str:
        return f"sftp://{self.config.username}@{self.config.host}:{self.config.port}{self.uri}"

    def _create_progress_handler(self, local_file_path: str):
        previous_bytes_copied = 0

        def progress_handler(bytes_copied, total_bytes):
            nonlocal previous_bytes_copied
            if bytes_copied - previous_bytes_copied >= 100 * 1024 * 1024:
                self.logger.info(
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
                self.logger.info(
                    f"Available disk space: {available_disk_space / (1024 * 1024):,.2f} MB ({available_disk_space / (1024 * 1024 * 1024):.2f} GB), "
                    f"available memory: {available_memory / (1024 * 1024):,.2f} MB ({available_memory / (1024 * 1024 * 1024):.2f} GB)."
                )

        return progress_handler

    def download_to_local_directory(self, local_file_path: str) -> None:
        # Get available disk space
        disk_usage = psutil.disk_usage("/")
        available_disk_space = disk_usage.free

        # Get available memory
        memory_info = psutil.virtual_memory()
        available_memory = memory_info.available

        # Log file size, available disk space, and memory
        file_size = self.size
        self.logger.info(
            f"Starting to download the file {self.uri} with size: {file_size / (1024 * 1024):,.2f} MB ({file_size / (1024 * 1024 * 1024):.2f} GB) "
            f"to '{local_file_path}' "
            f"with size: {file_size / (1024 * 1024):,.2f} MB ({file_size / (1024 * 1024 * 1024):.2f} GB), "
            f"available disk space: {available_disk_space / (1024 * 1024):,.2f} MB ({available_disk_space / (1024 * 1024 * 1024):.2f} GB),"
            f"available memory: {available_memory / (1024 * 1024):,.2f} MB ({available_memory / (1024 * 1024 * 1024):.2f} GB)."
        )
        progress_handler = self._create_progress_handler(local_file_path)
        # Copy a remote file in remote path from the SFTP server to the local host as local path.
        self.sftp_client.sftp_connection.get(self.uri, local_file_path, callback=progress_handler)


class SourceSFTPBulkStreamReader(AbstractFileBasedStreamReader):
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

    @staticmethod
    def _directory_could_match_globs(dir_path: str, globs: List[str], root_folder: str) -> bool:
        """
        Check if this directory path could potentially contain files matching any of the globs.
        Returns True if we should traverse this directory, False to skip it entirely.

        Examples:
            - dir_path="/data/2024", glob="/data/2024/*.csv" -> True (exact match)
            - dir_path="/data", glob="/data/2024/*.csv" -> True (prefix of match)
            - dir_path="/logs", glob="/data/**/*.csv" -> False (cannot match)
            - dir_path="/anything", glob="**/*.csv" -> True (recursive wildcard)
            - dir_path="/data", glob="/*/folder/folder2/*" -> True (could lead to match)
            - dir_path="/data/folder", glob="/*/folder/folder2/*" -> True (partial match)
        """
        for glob_pattern in globs:
            # Handle recursive wildcard - it matches everything
            if "**" in glob_pattern:
                # Extract the prefix before **
                prefix = glob_pattern.split("**")[0].rstrip("/")
                if not prefix or dir_path.startswith(prefix) or prefix.startswith(dir_path):
                    return True

            # Extract directory part from glob (everything before the last /)
            if "/" in glob_pattern:
                glob_dir = glob_pattern.rsplit("/", 1)[0]

                # For patterns without wildcards, use simple string matching
                if "*" not in glob_dir:
                    # Check if dir_path could lead to matching files
                    if glob_dir.startswith(dir_path):
                        # glob_dir is deeper than or equal to dir_path, so dir_path could lead to matches
                        return True
                    elif dir_path.startswith(glob_dir):
                        # dir_path is deeper than glob_dir
                        # Only traverse if dir_path equals glob_dir (we're at the right level)
                        # Don't traverse if dir_path is deeper (e.g., /data/2024/subdir for glob /data/2024/*.csv)
                        return dir_path == glob_dir
                else:
                    # For patterns with wildcards in directory positions (e.g., /*/folder/folder2/*)
                    # we need to check if this directory could be part of a matching path

                    # Check if the directory exactly matches the pattern
                    if globmatch(dir_path, glob_dir, flags=GLOBSTAR):
                        return True

                    # Count depth: if dir is shallower than the pattern, check if it could lead to a match
                    dir_depth = dir_path.count("/")
                    glob_depth = glob_dir.count("/")

                    if dir_depth <= glob_depth:
                        # Try to match the directory against the partial glob pattern
                        # by checking if the parts we have so far are compatible
                        glob_parts = glob_dir.split("/")
                        dir_parts = dir_path.split("/")

                        # Check if each directory part matches the corresponding glob part
                        could_match = True
                        for i, dir_part in enumerate(dir_parts):
                            if i < len(glob_parts):
                                glob_part = glob_parts[i]
                                # Skip empty parts (from leading slashes)
                                if dir_part == "" and glob_part == "":
                                    continue
                                # Check if this part could match (including wildcards)
                                if glob_part == "*":
                                    # Wildcard matches anything (single level)
                                    continue
                                elif glob_part == "**":
                                    # Recursive wildcard matches anything
                                    return True
                                elif not globmatch(dir_part, glob_part):
                                    # This part doesn't match the pattern
                                    could_match = False
                                    break

                        if could_match:
                            return True
            else:
                # Glob has no directory component (e.g., "*.csv")
                # Only matches files in the root folder
                if dir_path == root_folder:
                    return True

        return False

    def get_matching_files(
        self,
        globs: List[str],
        prefix: Optional[str],
        logger: logging.Logger,
    ) -> Iterable[SFTPBulkUploadableRemoteFile]:
        root_folder = self._config.folder_path or "/"
        directories = [root_folder]
        files_batch = []
        BATCH_SIZE = 100  # Process files in batches to reduce overhead

        # Normalize globs to handle root folder correctly
        normalized_globs = []
        for glob_pattern in globs:
            # Clean up multiple consecutive slashes (e.g., // -> /)
            # This can happen when patterns are constructed or user-provided
            while "//" in glob_pattern:
                glob_pattern = glob_pattern.replace("//", "/")

            # If glob doesn't start with /, make it relative to root_folder
            if not glob_pattern.startswith("/"):
                normalized_globs.append(f"{root_folder.rstrip('/')}/{glob_pattern}")
            else:
                normalized_globs.append(glob_pattern)

        # Iterate through directories and subdirectories
        while directories:
            current_dir = directories.pop()
            try:
                for item in self.sftp_client.sftp_connection.listdir_iter(current_dir):
                    if item.st_mode and stat.S_ISDIR(item.st_mode):
                        dir_path = f"{current_dir.rstrip('/')}/{item.filename}"
                        # Only traverse directories that could contain matching files
                        if self._directory_could_match_globs(dir_path, normalized_globs, root_folder):
                            directories.append(dir_path)
                        else:
                            logger.debug(f"Skipping directory {dir_path} (no globs match)")
                    else:
                        file_uri = f"{current_dir}/{item.filename}"
                        file_mtime = datetime.fromtimestamp(item.st_mtime)

                        file = SFTPBulkUploadableRemoteFile(
                            sftp_client=self.sftp_client,
                            logger=logger,
                            uri=file_uri,
                            last_modified=file_mtime,
                            updated_at=file_mtime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                            config=self.config,
                        )
                        files_batch.append(file)

                        # Process batch when it reaches BATCH_SIZE
                        if len(files_batch) >= BATCH_SIZE:
                            yield from self.filter_files_by_globs_and_start_date(
                                files_batch,
                                globs,
                            )
                            files_batch = []
            except Exception as e:
                logger.warning(f"Error listing directory {current_dir}: {e}")
                continue

        # Process remaining files
        if files_batch:
            yield from self.filter_files_by_globs_and_start_date(
                files_batch,
                globs,
            )

    def open_file(self, file: SFTPBulkUploadableRemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        remote_file = self.sftp_client.sftp_connection.open(file.uri, mode=mode.value)
        return remote_file
