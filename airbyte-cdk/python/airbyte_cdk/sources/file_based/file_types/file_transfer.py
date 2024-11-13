#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
import os
from typing import Any, Dict, Iterable

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.remote_file import RemoteFile

AIRBYTE_STAGING_DIRECTORY = os.getenv("AIRBYTE_STAGING_DIRECTORY", "/staging/files")
DEFAULT_LOCAL_DIRECTORY = "/tmp/airbyte-file-transfer"


class FileTransfer:
    def __init__(self) -> None:
        self._local_directory = AIRBYTE_STAGING_DIRECTORY if os.path.exists(AIRBYTE_STAGING_DIRECTORY) else DEFAULT_LOCAL_DIRECTORY

    def get_file(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Iterable[Dict[str, Any]]:
        try:
            yield stream_reader.get_file(file=file, local_directory=self._local_directory, logger=logger)
        except Exception as ex:
            logger.error("An error has occurred while getting file: %s", str(ex))
            raise ex
