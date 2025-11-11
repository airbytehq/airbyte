#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Iterable, Tuple

from airbyte_cdk.models import AirbyteRecordMessageFileReference
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_record_data import FileRecordData
from airbyte_cdk.sources.file_based.remote_file import UploadableRemoteFile
from airbyte_cdk.sources.utils.files_directory import get_files_directory


class FileTransfer:
    def __init__(self) -> None:
        self._local_directory = get_files_directory()

    def upload(
        self,
        file: UploadableRemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Iterable[Tuple[FileRecordData, AirbyteRecordMessageFileReference]]:
        try:
            yield stream_reader.upload(
                file=file, local_directory=self._local_directory, logger=logger
            )
        except Exception as ex:
            logger.error("An error has occurred while getting file: %s", str(ex))
            raise ex
