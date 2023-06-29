#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from functools import cached_property
from typing import Any, Dict, Iterable, List, Mapping, Optional, Type

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError, UndefinedParserError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_validation_policies import AbstractSchemaValidationPolicy
from airbyte_cdk.sources.file_based.stream.file_based_stream_config import FileBasedStreamConfig, PrimaryKeyType
from airbyte_cdk.sources.file_based.types import StreamSlice, StreamState
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
        validation_policies: Type[AbstractSchemaValidationPolicy],
    ):
        super().__init__()
        self.config = config
        self._catalog_schema = {}  # TODO: wire through configured catalog
        self._stream_reader = stream_reader
        self._discovery_policy = discovery_policy
        self._availability_strategy = availability_strategy
        self._parsers = parsers
        self.validation_policy = validation_policies(self.config.validation_policy)

    @property
    @abstractmethod
    def primary_key(self) -> PrimaryKeyType:
        ...

    @abstractmethod
    def list_files(self) -> List[RemoteFile]:
        """
        List all files that belong to the stream.
        """
        ...

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Optional[StreamSlice] = None,
        stream_state: Optional[StreamState] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Yield all records from all remote files in `list_files_for_this_sync`.
        This method acts as an adapter between the generic Stream interface and the file-based's
        stream since file-based streams manage their own states.
        """
        return self.read_records_from_slice(stream_slice)

    @abstractmethod
    def read_records_from_slice(self, stream_slice: StreamSlice) -> Iterable[Mapping[str, Any]]:
        """
        Yield all records from all remote files in `list_files_for_this_sync`.
        """
        ...

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: StreamState = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        This method acts as an adapter between the generic Stream interface and the file-based's
        stream since file-based streams manage their own states.
        """
        return self.compute_slices()

    @abstractmethod
    def compute_slices(self) -> Iterable[Optional[StreamSlice]]:
        """
        Return a list of slices that will be used to read files in the current sync.
        :return: The slices to use for the current sync.
        """
        ...

    @abstractmethod
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Return the JSON Schema for a stream.
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
            raise UndefinedParserError(FileBasedSourceError.UNDEFINED_PARSER, stream=self.name, file_type=file_type)

    def record_passes_validation_policy(self, record: Mapping[str, Any]) -> bool:
        return self.validation_policy.record_passes_validation_policy(record, self.get_json_schema())

    @cached_property
    def availability_strategy(self):
        return self._availability_strategy

    @property
    def name(self) -> str:
        return self.config.name
