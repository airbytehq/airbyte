#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.remote_file import RemoteFile

Schema = Dict[str, str]
Record = Dict[str, Any]


class FileTypeParser(ABC):
    """
    An abstract class containing methods that must be implemented for each
    supported file type.
    """

    @abstractmethod
    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Schema:
        """
        Infer the JSON Schema for this file.
        """
        ...

    @abstractmethod
    def parse_records(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> Iterable[Record]:
        """
        Parse and emit each record.
        """
        ...
