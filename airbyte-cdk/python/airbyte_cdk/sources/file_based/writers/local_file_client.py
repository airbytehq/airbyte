# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import os
from typing import Optional, Union, Any, Mapping

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.config.clients_config.local_sync_config import LocalSyncConfig

AIRBYTE_STAGING_DIRECTORY = os.getenv("AIRBYTE_STAGING_DIRECTORY", "/staging/files")
DEFAULT_LOCAL_DIRECTORY = "/tmp/airbyte-file-transfer"

class LocalFileTransferClient:
    def __init__(self, config: Optional[Union[LocalSyncConfig, Mapping[str, Any]]] = None):
        """
        Initialize the LocalFileTransferClient. It uses a default local directory for file saving.
        """
        self._config = config
        self._local_directory = AIRBYTE_STAGING_DIRECTORY if os.path.exists(AIRBYTE_STAGING_DIRECTORY) else DEFAULT_LOCAL_DIRECTORY

    @property
    def connection(self) -> None:
        """
        No connection is needed for local file writing.
        """
        return None

    @classmethod
    def get_client(cls, config: AbstractFileBasedSpec):
        """
        Return an instance of the LocalFileTransferClient.
        """
        return cls(config.sync_config)

    def write(self, file_uri: str, fp, file_size: int, logger: logging.Logger):
        """
        Write the file to a local directory.
        """
        # Remove left slashes from source path format to make relative path for writing locally
        file_relative_path = file_uri.lstrip("/")
        local_file_path = os.path.join(self._local_directory, file_relative_path)

        # Ensure the local directory exists
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # Get the absolute path
        absolute_file_path = os.path.abspath(local_file_path)

        logger.info(f"Writing file to {local_file_path}.")

        with open(local_file_path, "wb") as f:
            f.write(fp.read())
        logger.info(f"File {file_relative_path} successfully written to {self._local_directory}.")

        return {"file_url": absolute_file_path, "bytes": file_size, "file_relative_path": file_relative_path}
