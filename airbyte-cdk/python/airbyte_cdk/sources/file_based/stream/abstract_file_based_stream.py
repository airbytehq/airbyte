#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from functools import cache, cached_property, lru_cache
from typing import Any, Dict, Iterable, List, Mapping, Optional, Type

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.file_based.availability_strategy import AbstractFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig, PrimaryKeyType
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy
from airbyte_cdk.sources.file_based.exceptions import FileBasedErrorsCollector, FileBasedSourceError, RecordParseError, UndefinedParserError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_validation_policies import AbstractSchemaValidationPolicy
from airbyte_cdk.sources.file_based.stream.cursor import AbstractFileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamSlice
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.checkpoint import Cursor
from deprecated import deprecated


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
    - A dictionary of FileType:Parser that holds all the file types that can be handled
      by the stream.
    """

    def __init__(
        self,
        config: FileBasedStreamConfig,
        catalog_schema: Optional[Mapping[str, Any]],
        stream_reader: AbstractFileBasedStreamReader,
        availability_strategy: AbstractFileBasedAvailabilityStrategy,
        discovery_policy: AbstractDiscoveryPolicy,
        parsers: Dict[Type[Any], FileTypeParser],
        validation_policy: AbstractSchemaValidationPolicy,
        errors_collector: FileBasedErrorsCollector,
        cursor: AbstractFileBasedCursor,
    ):
        super().__init__()
        self.config = config
        self.catalog_schema = catalog_schema
        self.validation_policy = validation_policy
        self.stream_reader = stream_reader
        self._discovery_policy = discovery_policy
        self._availability_strategy = availability_strategy
        self._parsers = parsers
        self.errors_collector = errors_collector
        self._cursor = cursor

    @property
    @abstractmethod
    def primary_key(self) -> PrimaryKeyType:
        ...

    @cache
    def list_files(self) -> List[RemoteFile]:
        """
        List all files that belong to the stream.

        The output of this method is cached so we don't need to list the files more than once.
        This means we won't pick up changes to the files during a sync. This method uses the
        get_files method which is implemented by the concrete stream class.
        """
        return list(self.get_files())

    @abstractmethod
    def get_files(self) -> Iterable[RemoteFile]:
        """
        List all files that belong to the stream as defined by the stream's globs.
        """
        ...

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[StreamSlice] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Yield all records from all remote files in `list_files_for_this_sync`.
        This method acts as an adapter between the generic Stream interface and the file-based's
        stream since file-based streams manage their own states.
        """
        if stream_slice is None:
            raise ValueError("stream_slice must be set")
        return self.read_records_from_slice(stream_slice)

    @abstractmethod
    def read_records_from_slice(self, stream_slice: StreamSlice) -> Iterable[Mapping[str, Any]]:
        """
        Yield all records from all remote files in `list_files_for_this_sync`.
        """
        ...

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
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
    @lru_cache(maxsize=None)
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

    def get_parser(self) -> FileTypeParser:
        try:
            return self._parsers[type(self.config.format)]
        except KeyError:
            raise UndefinedParserError(FileBasedSourceError.UNDEFINED_PARSER, stream=self.name, format=type(self.config.format))

    def record_passes_validation_policy(self, record: Mapping[str, Any]) -> bool:
        if self.validation_policy:
            return self.validation_policy.record_passes_validation_policy(record=record, schema=self.catalog_schema)
        else:
            raise RecordParseError(
                FileBasedSourceError.UNDEFINED_VALIDATION_POLICY, stream=self.name, validation_policy=self.config.validation_policy
            )

    @cached_property
    @deprecated(version="3.7.0")
    def availability_strategy(self) -> AbstractFileBasedAvailabilityStrategy:
        return self._availability_strategy

    @property
    def name(self) -> str:
        return self.config.name

    def get_cursor(self) -> Optional[Cursor]:
        """
        This is a temporary hack. Because file-based, declarative, and concurrent have _slightly_ different cursor implementations
        the file-based cursor isn't compatible with the cursor-based iteration flow in core.py top-level CDK. By setting this to
        None, we defer to the regular incremental checkpoint flow. Once all cursors are consolidated under a common interface
        then this override can be removed.
        """
        return None
