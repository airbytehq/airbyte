#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
import logging
from functools import lru_cache
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

from typing_extensions import deprecated

from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteStream,
    ConfiguredAirbyteStream,
    Level,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import AbstractSource, Source
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.source import ExperimentalClassWarning
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.abstract_stream_facade import AbstractStreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor, FinalStateCursor
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.streams.concurrent.exceptions import ExceptionWithDisplayMessage
from airbyte_cdk.sources.streams.concurrent.helpers import (
    get_cursor_field_from_stream,
    get_primary_key_from_stream,
)
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.types import Record
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.utils.slice_hasher import SliceHasher

"""
This module contains adapters to help enabling concurrency on Stream objects without needing to migrate to AbstractStream
"""


@deprecated(
    "This class is experimental. Use at your own risk.",
    category=ExperimentalClassWarning,
)
class StreamFacade(AbstractStreamFacade[DefaultStream], Stream):
    """
    The StreamFacade is a Stream that wraps an AbstractStream and exposes it as a Stream.

    All methods either delegate to the wrapped AbstractStream or provide a default implementation.
    The default implementations define restrictions imposed on Streams migrated to the new interface. For instance, only source-defined cursors are supported.
    """

    @classmethod
    def create_from_stream(
        cls,
        stream: Stream,
        source: AbstractSource,
        logger: logging.Logger,
        state: Optional[MutableMapping[str, Any]],
        cursor: Cursor,
    ) -> Stream:
        """
        Create a ConcurrentStream from a Stream object.
        :param source: The source
        :param stream: The stream
        :param max_workers: The maximum number of worker thread to use
        :return:
        """
        pk = get_primary_key_from_stream(stream.primary_key)
        cursor_field = get_cursor_field_from_stream(stream)

        if not source.message_repository:
            raise ValueError(
                "A message repository is required to emit non-record messages. Please set the message repository on the source."
            )

        message_repository = source.message_repository
        return StreamFacade(
            DefaultStream(
                partition_generator=StreamPartitionGenerator(
                    stream,
                    message_repository,
                    SyncMode.full_refresh
                    if isinstance(cursor, FinalStateCursor)
                    else SyncMode.incremental,
                    [cursor_field] if cursor_field is not None else None,
                    state,
                ),
                name=stream.name,
                namespace=stream.namespace,
                json_schema=stream.get_json_schema(),
                primary_key=pk,
                cursor_field=cursor_field,
                logger=logger,
                cursor=cursor,
            ),
            stream,
            cursor,
            slice_logger=source._slice_logger,
            logger=logger,
        )

    @property
    def state(self) -> MutableMapping[str, Any]:
        raise NotImplementedError(
            "This should not be called as part of the Concurrent CDK code. Please report the problem to Airbyte"
        )

    @state.setter
    def state(self, value: Mapping[str, Any]) -> None:
        if "state" in dir(self._legacy_stream):
            self._legacy_stream.state = value  # type: ignore  # validating `state` is attribute of stream using `if` above

    def __init__(
        self,
        stream: DefaultStream,
        legacy_stream: Stream,
        cursor: Cursor,
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
                type=Type.LOG,
                log=AirbyteLogMessage(
                    level=Level.ERROR, message=f"Cursor State at time of exception: {state}"
                ),
            )
            raise exc

    def _read_records(self) -> Iterable[StreamData]:
        for partition in self._abstract_stream.generate_partitions():
            if self._slice_logger.should_log_slice_message(self._logger):
                yield self._slice_logger.create_slice_log_message(partition.to_slice())
            for record in partition.read():
                yield record.data

    @property
    def name(self) -> str:
        return self._abstract_stream.name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        # This method is not expected to be called directly. It is only implemented for backward compatibility with the old interface
        return self.as_airbyte_stream().source_defined_primary_key  # type: ignore # source_defined_primary_key is known to be an Optional[List[List[str]]]

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        if self._abstract_stream.cursor_field is None:
            return []
        else:
            return self._abstract_stream.cursor_field

    @property
    def cursor(self) -> Optional[Cursor]:  # type: ignore[override] # StreamFaced expects to use only airbyte_cdk.sources.streams.concurrent.cursor.Cursor
        return self._cursor

    # FIXME the lru_cache seems to be mostly there because of typing issue
    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        return self._abstract_stream.get_json_schema()

    @property
    def supports_incremental(self) -> bool:
        return self._legacy_stream.supports_incremental

    def as_airbyte_stream(self) -> AirbyteStream:
        return self._abstract_stream.as_airbyte_stream()

    def log_stream_sync_configuration(self) -> None:
        self._abstract_stream.log_stream_sync_configuration()

    def get_underlying_stream(self) -> DefaultStream:
        return self._abstract_stream


class SliceEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if hasattr(obj, "__json_serializable__"):
            return obj.__json_serializable__()

        # Let the base class default method raise the TypeError
        return super().default(obj)


class StreamPartition(Partition):
    """
    This class acts as an adapter between the new Partition interface and the Stream's stream_slice interface

    StreamPartitions are instantiated from a Stream and a stream_slice.

    This class can be used to help enable concurrency on existing connectors without having to rewrite everything as AbstractStream.
    In the long-run, it would be preferable to update the connectors, but we don't have the tooling or need to justify the effort at this time.
    """

    def __init__(
        self,
        stream: Stream,
        _slice: Optional[Mapping[str, Any]],
        message_repository: MessageRepository,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]],
        state: Optional[MutableMapping[str, Any]],
    ):
        """
        :param stream: The stream to delegate to
        :param _slice: The partition's stream_slice
        :param message_repository: The message repository to use to emit non-record messages
        """
        self._stream = stream
        self._slice = _slice
        self._message_repository = message_repository
        self._sync_mode = sync_mode
        self._cursor_field = cursor_field
        self._state = state
        self._hash = SliceHasher.hash(self._stream.name, self._slice)

    def read(self) -> Iterable[Record]:
        """
        Read messages from the stream.
        If the StreamData is a Mapping or an AirbyteMessage of type RECORD, it will be converted to a Record.
        Otherwise, the message will be emitted on the message repository.
        """
        try:
            # using `stream_state=self._state` have a very different behavior than the current one as today the state is updated slice
            #  by slice incrementally. We don't have this guarantee with Concurrent CDK. For HttpStream, `stream_state` is passed to:
            #  * fetch_next_page
            #  * parse_response
            #  Both are not used for Stripe so we should be good for the first iteration of Concurrent CDK. However, Stripe still do
            #  `if not stream_state` to know if it calls the Event stream or not
            for record_data in self._stream.read_records(
                cursor_field=self._cursor_field,
                sync_mode=SyncMode.full_refresh,
                stream_slice=copy.deepcopy(self._slice),
                stream_state=self._state,
            ):
                # Noting we'll also need to support FileTransferRecordMessage if we want to support file-based connectors in this facade
                # For now, file-based connectors have their own stream facade
                if isinstance(record_data, Mapping):
                    data_to_return = dict(record_data)
                    self._stream.transformer.transform(
                        data_to_return, self._stream.get_json_schema()
                    )
                    yield Record(
                        data=data_to_return,
                        stream_name=self.stream_name(),
                        associated_slice=self._slice,  # type: ignore [arg-type]
                    )
                elif isinstance(record_data, AirbyteMessage) and record_data.record is not None:
                    yield Record(
                        data=record_data.record.data or {},
                        stream_name=self.stream_name(),
                        associated_slice=self._slice,  # type: ignore [arg-type]
                    )
                else:
                    self._message_repository.emit_message(record_data)
        except Exception as e:
            display_message = self._stream.get_error_display_message(e)
            if display_message:
                raise ExceptionWithDisplayMessage(display_message) from e
            else:
                raise e

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._slice

    def __hash__(self) -> int:
        return self._hash

    def stream_name(self) -> str:
        return self._stream.name

    def __repr__(self) -> str:
        return f"StreamPartition({self._stream.name}, {self._slice})"


class StreamPartitionGenerator(PartitionGenerator):
    """
    This class acts as an adapter between the new PartitionGenerator and Stream.stream_slices

    This class can be used to help enable concurrency on existing connectors without having to rewrite everything as AbstractStream.
    In the long-run, it would be preferable to update the connectors, but we don't have the tooling or need to justify the effort at this time.
    """

    def __init__(
        self,
        stream: Stream,
        message_repository: MessageRepository,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]],
        state: Optional[MutableMapping[str, Any]],
    ):
        """
        :param stream: The stream to delegate to
        :param message_repository: The message repository to use to emit non-record messages
        """
        self.message_repository = message_repository
        self._stream = stream
        self._sync_mode = sync_mode
        self._cursor_field = cursor_field
        self._state = state

    def generate(self) -> Iterable[Partition]:
        for s in self._stream.stream_slices(
            sync_mode=self._sync_mode, cursor_field=self._cursor_field, stream_state=self._state
        ):
            yield StreamPartition(
                self._stream,
                copy.deepcopy(s),
                self.message_repository,
                self._sync_mode,
                self._cursor_field,
                self._state,
            )
