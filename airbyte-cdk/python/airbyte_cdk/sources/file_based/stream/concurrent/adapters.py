#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import copy
import logging
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, ConfiguredAirbyteStream, Level, SyncMode, Type
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.file_based.availability_strategy import (
    AbstractFileBasedAvailabilityStrategy,
    AbstractFileBasedAvailabilityStrategyWrapper,
)
from airbyte_cdk.sources.file_based.config.file_based_stream_config import PrimaryKeyType
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream
from airbyte_cdk.sources.file_based.stream.concurrent.cursor import FileBasedFinalStateCursor
from airbyte_cdk.sources.file_based.stream.cursor import AbstractFileBasedCursor
from airbyte_cdk.sources.file_based.types import StreamSlice
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.source import ExperimentalClassWarning
from airbyte_cdk.sources.streams.concurrent.abstract_stream_facade import AbstractStreamFacade
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.streams.concurrent.exceptions import ExceptionWithDisplayMessage
from airbyte_cdk.sources.streams.concurrent.helpers import get_cursor_field_from_stream, get_primary_key_from_stream
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from deprecated.classic import deprecated

if TYPE_CHECKING:
    from airbyte_cdk.sources.file_based.stream.concurrent.cursor import AbstractConcurrentFileBasedCursor

"""
This module contains adapters to help enabling concurrency on File-based Stream objects without needing to migrate to AbstractStream
"""


@deprecated("This class is experimental. Use at your own risk.", category=ExperimentalClassWarning)
class FileBasedStreamFacade(AbstractStreamFacade[DefaultStream], AbstractFileBasedStream):
    @classmethod
    def create_from_stream(
        cls,
        stream: AbstractFileBasedStream,
        source: AbstractSource,
        logger: logging.Logger,
        state: Optional[MutableMapping[str, Any]],
        cursor: "AbstractConcurrentFileBasedCursor",
    ) -> "FileBasedStreamFacade":
        """
        Create a ConcurrentStream from a FileBasedStream object.
        """
        pk = get_primary_key_from_stream(stream.primary_key)
        cursor_field = get_cursor_field_from_stream(stream)
        stream._cursor = cursor

        if not source.message_repository:
            raise ValueError(
                "A message repository is required to emit non-record messages. Please set the message repository on the source."
            )

        message_repository = source.message_repository
        return FileBasedStreamFacade(
            DefaultStream(
                partition_generator=FileBasedStreamPartitionGenerator(
                    stream,
                    message_repository,
                    SyncMode.full_refresh if isinstance(cursor, FileBasedFinalStateCursor) else SyncMode.incremental,
                    [cursor_field] if cursor_field is not None else None,
                    state,
                    cursor,
                ),
                name=stream.name,
                json_schema=stream.get_json_schema(),
                availability_strategy=AbstractFileBasedAvailabilityStrategyWrapper(stream),
                primary_key=pk,
                cursor_field=cursor_field,
                logger=logger,
                namespace=stream.namespace,
                cursor=cursor,
            ),
            stream,
            cursor,
            logger=logger,
            slice_logger=source._slice_logger,
        )

    def __init__(
        self,
        stream: DefaultStream,
        legacy_stream: AbstractFileBasedStream,
        cursor: AbstractFileBasedCursor,
        slice_logger: SliceLogger,
        logger: logging.Logger,
    ):
        """
        :param stream: The underlying AbstractStream
        """
        self._abstract_stream = stream
        self._legacy_stream = legacy_stream
        self._cursor = cursor
        self._slice_logger = slice_logger
        self._logger = logger
        self.catalog_schema = legacy_stream.catalog_schema
        self.config = legacy_stream.config
        self.validation_policy = legacy_stream.validation_policy

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        if self._abstract_stream.cursor_field is None:
            return []
        else:
            return self._abstract_stream.cursor_field

    @property
    def name(self) -> str:
        return self._abstract_stream.name

    @property
    def supports_incremental(self) -> bool:
        return self._legacy_stream.supports_incremental

    @property
    @deprecated(version="3.7.0")
    def availability_strategy(self) -> AbstractFileBasedAvailabilityStrategy:
        return self._legacy_stream.availability_strategy

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        return self._abstract_stream.get_json_schema()

    @property
    def primary_key(self) -> PrimaryKeyType:
        return self._legacy_stream.config.primary_key or self.get_parser().get_parser_defined_primary_key(self._legacy_stream.config)

    def get_parser(self) -> FileTypeParser:
        return self._legacy_stream.get_parser()

    def get_files(self) -> Iterable[RemoteFile]:
        return self._legacy_stream.get_files()

    def read_records_from_slice(self, stream_slice: StreamSlice) -> Iterable[Mapping[str, Any]]:
        yield from self._legacy_stream.read_records_from_slice(stream_slice)

    def compute_slices(self) -> Iterable[Optional[StreamSlice]]:
        return self._legacy_stream.compute_slices()

    def infer_schema(self, files: List[RemoteFile]) -> Mapping[str, Any]:
        return self._legacy_stream.infer_schema(files)

    def get_underlying_stream(self) -> DefaultStream:
        return self._abstract_stream

    def read(
        self,
        configured_stream: ConfiguredAirbyteStream,
        logger: logging.Logger,
        slice_logger: SliceLogger,
        stream_state: MutableMapping[str, Any],
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ) -> Iterable[StreamData]:
        yield from self._read_records()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        try:
            yield from self._read_records()
        except Exception as exc:
            if hasattr(self._cursor, "state"):
                state = str(self._cursor.state)
            else:
                # This shouldn't happen if the ConcurrentCursor was used
                state = "unknown; no state attribute was available on the cursor"
            yield AirbyteMessage(
                type=Type.LOG, log=AirbyteLogMessage(level=Level.ERROR, message=f"Cursor State at time of exception: {state}")
            )
            raise exc

    def _read_records(self) -> Iterable[StreamData]:
        for partition in self._abstract_stream.generate_partitions():
            if self._slice_logger.should_log_slice_message(self._logger):
                yield self._slice_logger.create_slice_log_message(partition.to_slice())
            for record in partition.read():
                yield record.data


class FileBasedStreamPartition(Partition):
    def __init__(
        self,
        stream: AbstractFileBasedStream,
        _slice: Optional[Mapping[str, Any]],
        message_repository: MessageRepository,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]],
        state: Optional[MutableMapping[str, Any]],
        cursor: "AbstractConcurrentFileBasedCursor",
    ):
        self._stream = stream
        self._slice = _slice
        self._message_repository = message_repository
        self._sync_mode = sync_mode
        self._cursor_field = cursor_field
        self._state = state
        self._cursor = cursor
        self._is_closed = False

    def read(self) -> Iterable[Record]:
        try:
            for record_data in self._stream.read_records(
                cursor_field=self._cursor_field,
                sync_mode=SyncMode.full_refresh,
                stream_slice=copy.deepcopy(self._slice),
                stream_state=self._state,
            ):
                if isinstance(record_data, Mapping):
                    data_to_return = dict(record_data)
                    self._stream.transformer.transform(data_to_return, self._stream.get_json_schema())
                    yield Record(data_to_return, self.stream_name())
                elif isinstance(record_data, AirbyteMessage) and record_data.type == Type.RECORD:
                    # `AirbyteMessage`s of type `Record` should also be yielded so they are enqueued
                    yield Record(record_data.record.data, self.stream_name())
                else:
                    self._message_repository.emit_message(record_data)
        except Exception as e:
            display_message = self._stream.get_error_display_message(e)
            if display_message:
                raise ExceptionWithDisplayMessage(display_message) from e
            else:
                raise e

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        if self._slice is None:
            return None
        assert (
            len(self._slice["files"]) == 1
        ), f"Expected 1 file per partition but got {len(self._slice['files'])} for stream {self.stream_name()}"
        file = self._slice["files"][0]
        return {"files": [file]}

    def close(self) -> None:
        self._cursor.close_partition(self)
        self._is_closed = True

    def is_closed(self) -> bool:
        return self._is_closed

    def __hash__(self) -> int:
        if self._slice:
            # Convert the slice to a string so that it can be hashed
            if len(self._slice["files"]) != 1:
                raise ValueError(
                    f"Slices for file-based streams should be of length 1, but got {len(self._slice['files'])}. This is unexpected. Please contact Support."
                )
            else:
                s = f"{self._slice['files'][0].last_modified.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}_{self._slice['files'][0].uri}"
            return hash((self._stream.name, s))
        else:
            return hash(self._stream.name)

    def stream_name(self) -> str:
        return self._stream.name

    def __repr__(self) -> str:
        return f"FileBasedStreamPartition({self._stream.name}, {self._slice})"


class FileBasedStreamPartitionGenerator(PartitionGenerator):
    def __init__(
        self,
        stream: AbstractFileBasedStream,
        message_repository: MessageRepository,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]],
        state: Optional[MutableMapping[str, Any]],
        cursor: "AbstractConcurrentFileBasedCursor",
    ):
        self._stream = stream
        self._message_repository = message_repository
        self._sync_mode = sync_mode
        self._cursor_field = cursor_field
        self._state = state
        self._cursor = cursor

    def generate(self) -> Iterable[FileBasedStreamPartition]:
        pending_partitions = []
        for _slice in self._stream.stream_slices(sync_mode=self._sync_mode, cursor_field=self._cursor_field, stream_state=self._state):
            if _slice is not None:
                for file in _slice.get("files", []):
                    pending_partitions.append(
                        FileBasedStreamPartition(
                            self._stream,
                            {"files": [copy.deepcopy(file)]},
                            self._message_repository,
                            self._sync_mode,
                            self._cursor_field,
                            self._state,
                            self._cursor,
                        )
                    )
        self._cursor.set_pending_partitions(pending_partitions)
        yield from pending_partitions
