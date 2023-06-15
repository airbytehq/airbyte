#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from functools import cached_property
from typing import Any, Dict, Iterable, List, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy
from airbyte_cdk.sources.file_based.exceptions import UndefinedParserError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream.file_based_stream_config import FileBasedStreamConfig, PrimaryKeyType
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy


class AbstractFileBasedStream(Stream):
    """
    A file-based stream in an Airbyte source.

    In addition to the base Stream attributes, a file-based stream has
    - A config object (derived from the corresponding stream section in source config).
      This contains the globs defining the stream's files.
    - A StreamReader, which knows how to list and open files in the stream.
    - A FileBasedAvailabilityStrategy, which knows how to verify that we can list and open
      files in the stream.
    - A DiscoveryPolicy that controls the number of concurrent requests sent to the source
      during discover, and the number of files used for schema discovery.
    - A dictionary of FileType:Parser that holds all of the file types that can be handled
      by the stream.
    """

    def __init__(
        self,
        config: FileBasedStreamConfig,
        stream_reader: AbstractFileBasedStreamReader,
        availability_strategy: AvailabilityStrategy,
        discovery_policy: AbstractDiscoveryPolicy,
        parsers: Dict[str, FileTypeParser],
    ):
        super().__init__()
        self.config = config
        self._catalog_schema = {}  # TODO: wire through configured catalog
        self._stream_reader = stream_reader
        self._discovery_policy = discovery_policy
        self._availability_strategy = availability_strategy
        self._parsers = parsers

    @property
    @abstractmethod
    def primary_key(self) -> PrimaryKeyType:
        ...

    @abstractmethod
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Optional[StreamSlice] = None,
        stream_state: Optional[StreamState] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Yield all records from all remote files in `list_files_for_this_sync`.
        """
        ...

    @abstractmethod
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Return the JSON Schema for a stream.
        """
        ...

    @abstractmethod
    def list_files(self) -> List[RemoteFile]:
        """
        List all files that belong to the stream.
        """
        ...

    @abstractmethod
    def list_files_for_this_sync(self, stream_slice: Optional[StreamSlice]) -> Iterable[RemoteFile]:
        """
        Return the subset of this stream's files that will be read in the current sync.
        """
        ...

    @abstractmethod
    def infer_schema(self, files: List[RemoteFile]) -> Mapping[str, Any]:
        """
        Infer the schema for files in the stream.
        """
        ...

    def get_parser(self, file_type: str) -> FileTypeParser:
        try:
            return self._parsers[file_type]
        except KeyError:
            raise UndefinedParserError(f"No parser is defined for file type {file_type}.")

    @cached_property
    def availability_strategy(self):
        return self._availability_strategy

    @property
    def name(self) -> str:
        return self.config.name
