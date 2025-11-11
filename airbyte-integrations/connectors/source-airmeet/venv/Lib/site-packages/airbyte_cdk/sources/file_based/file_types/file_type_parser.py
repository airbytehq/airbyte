#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import (
    AbstractFileBasedStreamReader,
    FileReadMode,
)
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import SchemaType

Record = Dict[str, Any]


class FileTypeParser(ABC):
    """
    An abstract class containing methods that must be implemented for each
    supported file type.
    """

    @property
    def parser_max_n_files_for_schema_inference(self) -> Optional[int]:
        """
        The discovery policy decides how many files are loaded for schema inference. This method can provide a parser-specific override. If it's defined, the smaller of the two values will be used.
        """
        return None

    @property
    def parser_max_n_files_for_parsability(self) -> Optional[int]:
        """
        The availability policy decides how many files are loaded for checking whether parsing works correctly. This method can provide a parser-specific override. If it's defined, the smaller of the two values will be used.
        """
        return None

    def get_parser_defined_primary_key(self, config: FileBasedStreamConfig) -> Optional[str]:
        """
        The parser can define a primary key. If no user-defined primary key is provided, this will be used.
        """
        return None

    @abstractmethod
    def check_config(self, config: FileBasedStreamConfig) -> Tuple[bool, Optional[str]]:
        """
        Check whether the config is valid for this file type. If it is, return True and None. If it's not, return False and an error message explaining why it's invalid.
        """
        return True, None

    @abstractmethod
    async def infer_schema(
        self,
        config: FileBasedStreamConfig,
        file: RemoteFile,
        stream_reader: AbstractFileBasedStreamReader,
        logger: logging.Logger,
    ) -> SchemaType:
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
        discovered_schema: Optional[Mapping[str, SchemaType]],
    ) -> Iterable[Record]:
        """
        Parse and emit each record.
        """
        ...

    @property
    @abstractmethod
    def file_read_mode(self) -> FileReadMode:
        """
        The mode in which the file should be opened for reading.
        """
        ...
