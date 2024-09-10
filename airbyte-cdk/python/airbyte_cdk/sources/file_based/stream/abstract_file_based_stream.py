#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import datetime
import logging
import sys
from abc import abstractmethod
from collections.abc import MutableMapping
from functools import cache, cached_property, lru_cache
from typing import Any, Dict, Iterable, List, Mapping, Optional, TextIO, Type

import polars as pl
from deprecated import deprecated

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteStream, SyncMode
from airbyte_cdk.models import Type as _AirbyteMessageType
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.file_based.availability_strategy import AbstractFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.config.file_based_stream_config import BulkMode, FileBasedStreamConfig, PrimaryKeyType
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
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import SliceLogger


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

    def read(
        self,
        configured_stream: ConfiguredAirbyteStream,
        logger: logging.Logger,
        slice_logger: SliceLogger,
        stream_state: MutableMapping[str, Any],
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ) -> Iterable[StreamData]:
        if not self.config.bulk_mode or self.config.bulk_mode == BulkMode.DISABLED:
            # Use the default `Stream.read()` method if bulk mode is disabled.
            return super().read(
                configured_stream=configured_stream,
                logger=logger,
                slice_logger=slice_logger,
                stream_state=stream_state,
                state_manager=state_manager,
                internal_config=internal_config,
            )

        return self._bulk_read(
            configured_stream=configured_stream,
            logger=logger,
            slice_logger=slice_logger,
            stream_state=stream_state,
            state_manager=state_manager,
            internal_config=internal_config,
        )

    def _records_df_to_record_messages(
        self,
        dataframe: pl.DataFrame | pl.LazyFrame,
    ) -> Iterable[AirbyteMessage]:
        if isinstance(dataframe, pl.LazyFrame):
            # Stream from the LazyFrame in chunks
            # TODO: This is cheating for now. We just put it in a single dataframe.
            # Note that this will fail if there is not enough memory.
            stream = [dataframe.collect()]

            for chunk in stream:
                # Recursively process each chunk as a DataFrame
                yield from self._records_df_to_record_messages(
                    dataframe=chunk,
                )
            return

        # If DataFrame, iterate over rows and create AirbyteMessages
        record_generator = (
            AirbyteMessage(
                type=_AirbyteMessageType.RECORD,
                record=AirbyteRecordMessage(
                    stream=self.name,
                    data=record_data,
                    emitted_at=int(datetime.datetime.now().timestamp()) * 1000,
                ),
            )
            # TODO: Consider named=False for better performance (but we need to manually map field names)
            for record_data in dataframe.iter_rows(named=True)
        )
        # Uncomment for debugging:
        # all_records = list(record_generator)
        yield from record_generator

    def _bulk_read(
        self,
        configured_stream: ConfiguredAirbyteStream,
        logger: logging.Logger,
        slice_logger: SliceLogger,
        stream_state: MutableMapping[str, Any],
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ) -> Iterable[AirbyteMessage]:
        """Similar to the default `Stream.read()` method, but for bulk mode streams.

        This method will return iterable AirbyteMessages, and not StreamData. Callers can
        emit these messages directly to the output without further processing. This
        is to take advantage of the bulk processing capabilities of file-based streams.
        """
        # Else we are in bulk mode, so we need to use the file-based read method.

        ############################################################################################
        # READER'S NOTE: The below was copied from the default `Stream.read()` method and modified
        #                to use the file-based read method.
        ############################################################################################

        sync_mode = configured_stream.sync_mode
        cursor_field = configured_stream.cursor_field
        self.configured_json_schema = configured_stream.stream.json_schema

        # WARNING: When performing a read() that uses incoming stream state, we MUST use the self.state that is defined as
        # opposed to the incoming stream_state value. Because some connectors like ones using the file-based CDK modify
        # state before setting the value on the Stream attribute, the most up-to-date state is derived from Stream.state
        # instead of the stream_state parameter. This does not apply to legacy connectors using get_updated_state().
        try:
            stream_state = self.state  # type: ignore # we know the field might not exist...
        except AttributeError:
            pass

        should_checkpoint = bool(state_manager)
        checkpoint_reader = self._get_checkpoint_reader(
            logger=logger, cursor_field=cursor_field, sync_mode=sync_mode, stream_state=stream_state
        )

        next_slice = checkpoint_reader.next()

        record_counter: int | None = None  # MODIFIED: preserve "None" if not doing inline tallies
        stream_state_tracker = copy.deepcopy(stream_state)
        while next_slice is not None:
            if slice_logger.should_log_slice_message(logger):
                yield slice_logger.create_slice_log_message(next_slice)

            ############################################################################################
            # READER'S NOTE: Nothing has been modified from the last note until here.
            ############################################################################################

            records_dfs: Iterable[pl.DataFrame | pl.LazyFrame] = self.read_records_as_dataframes(
                sync_mode=sync_mode,  # todo: change this interface to no longer rely on sync_mode for behavior
                stream_slice=next_slice,
                stream_state=stream_state,
                cursor_field=cursor_field or None,
            )

            for records_df in records_dfs:
                # Perform validation and envelope wrapping in bulk, then
                # emit the record messages.
                yield from self._records_df_to_record_messages(records_df)

                # if self.cursor_field:
                #     # TODO: Implement cursor tracking for file-based streams.
                #     # In theory, this could be the file modified timestamps, in which case we don't
                #     # need to do anything here.
                #     # It could also (in theory) be a column in the file, in which case we would need
                #     # to calculate max(self.cursor_field) for each dataframe, and use that to
                #     # update the state tracker.

                #     # OLD CODE:
                #     # stream_state_tracker = self.get_updated_state(stream_state_tracker, record_data)
                #     # self._observe_state(checkpoint_reader, stream_state_tracker)

                if isinstance(records_df, pl.DataFrame):
                    record_counter = (record_counter or 0) + records_df.shape[0]
                else:
                    # TODO: Need another way to count records.
                    pass

                # READER'S NOTE: Not changed below.

                checkpoint_interval = self.state_checkpoint_interval
                checkpoint = checkpoint_reader.get_checkpoint()
                if should_checkpoint and checkpoint_interval and record_counter % checkpoint_interval == 0 and checkpoint is not None:
                    airbyte_state_message = self._checkpoint_state(checkpoint, state_manager=state_manager)
                    yield airbyte_state_message

                if internal_config.is_limit_reached(record_counter):
                    break
                # READER'S NOTE: Not changed above, from last note until here.

            # TODO: Replace this with a dataframe 'max' operation, or similar:
            # self._observe_state(checkpoint_reader)
            checkpoint_state = checkpoint_reader.get_checkpoint()
            if should_checkpoint and checkpoint_state is not None:
                airbyte_state_message = self._checkpoint_state(checkpoint_state, state_manager=state_manager)
                yield airbyte_state_message

            next_slice = checkpoint_reader.next()

        checkpoint = checkpoint_reader.get_checkpoint()
        if should_checkpoint and checkpoint is not None:
            airbyte_state_message = self._checkpoint_state(checkpoint, state_manager=state_manager)
            yield airbyte_state_message

    def read_to_buffer(
        self,
        configured_stream: ConfiguredAirbyteStream,
        logger: logging.Logger,
        slice_logger: SliceLogger,
        stream_state: MutableMapping[str, Any],
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
        stdout_buffer: TextIO = sys.stdout,
    ) -> Iterable[AirbyteMessage]:
        """Bulk process data into messages, and write directly to the IO buffer."""
        raise NotImplementedError("Bulk processing to buffer is not yet implemented.")

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

    def read_records_as_dataframes(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[StreamSlice] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[pl.DataFrame | pl.LazyFrame]:
        """
        Yield dataframes from from all remote files in `list_files_for_this_sync`.
        This method acts as an adapter between the generic Stream interface and the file-based's
        stream since file-based streams manage their own states.
        """
        if stream_slice is None:
            raise ValueError("stream_slice must be set")

        return self.read_records_from_slice_as_dataframes(stream_slice)

    @abstractmethod
    def read_records_from_slice(self, stream_slice: StreamSlice) -> Iterable[Mapping[str, Any]]:
        """
        Yield all records from all remote files in `list_files_for_this_sync`.
        """
        ...

    @abstractmethod
    def read_records_from_slice_as_dataframes(
        self,
        stream_slice: StreamSlice,
    ) -> Iterable[pl.DataFrame | pl.LazyFrame]:
        """
        Yield dataframes from from all remote files in `list_files_for_this_sync`.
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
