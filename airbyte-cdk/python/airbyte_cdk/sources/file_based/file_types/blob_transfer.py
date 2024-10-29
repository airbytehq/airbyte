#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from io import IOBase
from typing import Any, Dict, Generator, Iterable, Optional, Tuple

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.writers.local_file_client import LocalFileTransferClient


class _FileReader:
    def read_data(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
        file_read_mode: FileReadMode,
    ) -> Generator[Tuple[IOBase, int], None, None]:

        try:
            file_size = stream_reader.file_size(file)
            with stream_reader.open_file(file, file_read_mode, "UTF-8", logger) as fp:
                yield fp, file_size

        except Exception as ex:
            logger.error("An error has occurred while reading file: %s", str(ex))


class BlobTransfer:
    def __init__(self, file_reader: Optional[_FileReader] = None):
        self._file_reader = file_reader if file_reader else _FileReader()

    def write_streams(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Iterable[Dict[str, Any]]:
        file_no = 0
        try:
            data_generator = self._file_reader.read_data(config, file, stream_reader, logger, self.file_read_mode)
            local_writer = LocalFileTransferClient()
            for file_opened, file_size in data_generator:
                yield local_writer.write(file.uri, file_opened, file_size, logger)
                file_no += 1
        except Exception as ex:
            logger.error("An error has occurred while writing file: %s", str(ex))
            raise ex
        finally:
            data_generator.close()

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ
