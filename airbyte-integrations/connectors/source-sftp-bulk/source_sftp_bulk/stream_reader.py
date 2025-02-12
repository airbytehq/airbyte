# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import datetime
import logging
import stat
import time
from io import IOBase
from typing import Dict, Iterable, List, Optional

import psutil
from typing_extensions import override

from airbyte_cdk import FailureType
from airbyte_cdk.sources.file_based.exceptions import FileSizeLimitError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
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

    def get_matching_files(
        self,
        globs: List[str],
        prefix: Optional[str],
        logger: logging.Logger,
    ) -> Iterable[RemoteFile]:
        directories = [self._config.folder_path or "/"]

        # Iterate through directories and subdirectories
        while directories:
            current_dir = directories.pop()
            try:
                items = self.sftp_client.sftp_connection.listdir_attr(current_dir)
            except Exception as e:
                logger.warning(f"Failed to list files in directory: {e}")
                continue

            for item in items:
                if item.st_mode and stat.S_ISDIR(item.st_mode):
                    directories.append(f"{current_dir}/{item.filename}")
                else:
                    yield from self.filter_files_by_globs_and_start_date(
                        [RemoteFile(uri=f"{current_dir}/{item.filename}", last_modified=datetime.datetime.fromtimestamp(item.st_mtime))],
                        globs,
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
    def get_file(self, file: RemoteFile, local_directory: str, logger: logging.Logger) -> Dict[str, str | int]:
        """
        Downloads a file from SFTP server to a specified local directory.

        Args:
            file (RemoteFile): The remote file object containing URI and metadata.
            local_directory (str): The local directory path where the file will be downloaded.
            logger (logging.Logger): Logger for logging information and errors.

        Returns:
            dict: A dictionary containing the following:
                - "file_url" (str): The absolute path of the downloaded file.
                - "bytes" (int): The file size in bytes.
                - "file_relative_path" (str): The relative path of the file for local storage. Is relative to local_directory as
                this a mounted volume in the pod container.

        Raises:
            FileSizeLimitError: If the file size exceeds the predefined limit (1 GB).
        """
        file_size = self.file_size(file)
        # I'm putting this check here so we can remove the safety wheels per connector when ready.
        if file_size > self.FILE_SIZE_LIMIT:
            message = "File size exceeds the 1 GB limit."
            raise FileSizeLimitError(message=message, internal_message=message, failure_type=FailureType.config_error)

        file_relative_path, local_file_path, absolute_file_path = self._get_file_transfer_paths(file, local_directory)

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

        return {"file_url": absolute_file_path, "bytes": file_size, "file_relative_path": file_relative_path}

    def file_size(self, file: RemoteFile):
        file_size = self.sftp_client.sftp_connection.stat(file.uri).st_size
        return file_size
