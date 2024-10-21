# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import datetime
import logging
import stat
from io import IOBase
from typing import Iterable, List, Optional

from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from source_sftp_bulk.client import SFTPClient
from source_sftp_bulk.spec import SourceSFTPBulkSpec


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
