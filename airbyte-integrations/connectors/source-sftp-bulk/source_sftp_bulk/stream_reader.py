# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import datetime
import logging
import stat
from io import IOBase
from typing import Any, Iterable, List, Optional

import psutil

from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import UploadableRemoteFile
from source_sftp_bulk.client import SFTPClient
from source_sftp_bulk.spec import SourceSFTPBulkSpec


class SFTPBulkUploadableRemoteFile(UploadableRemoteFile):
    sftp_client: Any
    logger: Any

    def __init__(self, sftp_client: SFTPClient, logger: logging.Logger, **kwargs):
        super().__init__(**kwargs)
        self.sftp_client = sftp_client
        self.logger = logger

    @property
    def size(self) -> int:
        file_size = self.sftp_client.sftp_connection.stat(self.uri).st_size
        return file_size

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

    def get_matching_files(
        self,
        globs: List[str],
        prefix: Optional[str],
        logger: logging.Logger,
    ) -> Iterable[SFTPBulkUploadableRemoteFile]:
        directories = [self._config.folder_path or "/"]

        # Iterate through directories and subdirectories
        while directories:
            current_dir = directories.pop()
            for item in self.sftp_client.sftp_connection.listdir_iter(current_dir):
                if item.st_mode and stat.S_ISDIR(item.st_mode):
                    directories.append(f"{current_dir}/{item.filename}")
                else:
                    file = SFTPBulkUploadableRemoteFile(
                        sftp_client=self.sftp_client,
                        logger=logger,
                        uri=f"{current_dir}/{item.filename}",
                        last_modified=datetime.datetime.fromtimestamp(item.st_mtime),
                        updated_at=datetime.datetime.fromtimestamp(item.st_mtime).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    )
                    yield from self.filter_files_by_globs_and_start_date(
                        [file],
                        globs,
                    )

    def open_file(self, file: SFTPBulkUploadableRemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        remote_file = self.sftp_client.sftp_connection.open(file.uri, mode=mode.value)
        return remote_file
