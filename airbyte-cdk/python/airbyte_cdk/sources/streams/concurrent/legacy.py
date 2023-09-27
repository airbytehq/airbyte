#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import copy
import json
import logging
from functools import lru_cache
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource, Source
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream, FieldPath
from airbyte_cdk.sources.streams.concurrent.availability_strategy import AbstractAvailabilityStrategy
from airbyte_cdk.sources.streams.concurrent.error_message_parser import ErrorMessageParser
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.thread_based_concurrent_stream import ThreadBasedConcurrentStream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from deprecated.classic import deprecated

"""
This module contains adapters to help enabling concurrency on existing Stream without needing to migrate to AbstractStream
"""


@deprecated("This class is experimental. Use at your own risk.")
class StreamFacade(Stream):
    """
    The StreamFacade is a Stream that wraps an AbstractStream and exposes it as a Stream.

    All methods either delegate to the wrapped AbstractStream or provide a default implementation.
    The default implementations define restrictions imposed on Streams migrated to the new interface. For instance, only source-defined cursors are supported.
    """

    @classmethod
    def create_from_legacy_stream(cls, stream: Stream, source: AbstractSource, max_workers: int) -> Stream:
        """
        Create a ConcurrentStream from a legacy Stream.
        :param source: The source
        :param stream: The stream
        :param max_workers: The maximum number of worker thread to use
        :return:
        """
        pk = cls._get_primary_key_from_stream(stream.primary_key)

        if isinstance(stream.cursor_field, list):
            if len(stream.cursor_field) > 1:
                raise ValueError(f"Nested cursor fields are not supported. Got {stream.cursor_field} for {stream.name}")
            elif len(stream.cursor_field) == 0:
                cursor_field = None
            else:
                cursor_field = stream.cursor_field[0]
        else:
            cursor_field = stream.cursor_field

        if not source.message_repository:
            raise ValueError(
                "A message repository is required to emit non-record messages. Please set the message repository on the source."
            )

        message_repository = source.message_repository
        return StreamFacade(
            ThreadBasedConcurrentStream(
                partition_generator=LegacyPartitionGenerator(stream, message_repository),
                max_workers=max_workers,
                name=stream.name,
                json_schema=stream.get_json_schema(),
                availability_strategy=LegacyAvailabilityStrategy(stream, source),
                primary_key=pk,
                cursor_field=cursor_field,
                error_display_message_parser=LegacyErrorMessageParser(stream),
                slice_logger=source._slice_logger,
                message_repository=message_repository,
            )
        )

    @classmethod
    def _get_primary_key_from_stream(cls, stream_primary_key: Optional[Union[str, List[str], List[List[str]]]]) -> Optional[FieldPath]:
        if stream_primary_key is None or isinstance(stream_primary_key, str):
            return stream_primary_key
        elif isinstance(stream_primary_key, list):
            if len(stream_primary_key) > 0 and all(isinstance(k, str) for k in stream_primary_key):
                return stream_primary_key  # type: ignore # We verified all items in the list are strings
            else:
                raise ValueError(f"Nested primary keys are not supported. Found {stream_primary_key}")
        else:
            raise ValueError(f"Invalid type for primary key: {stream_primary_key}")

    def __init__(self, stream: AbstractStream):
        self._stream = stream

    def read_full_refresh(
        self,
        cursor_field: Optional[List[str]],
        logger: logging.Logger,
        slice_logger: SliceLogger,
    ) -> Iterable[StreamData]:
        """
        Read full refresh. Delegate to the underlying AbstractStream, ignoring all the parameters
        :param cursor_field: (ignored)
        :param logger: (ignored)
        :param slice_logger: (ignored)
        :return: Iterable of StreamData
        """
        for record in self._stream.read():
            yield record.data

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        if sync_mode == SyncMode.full_refresh:
            for record in self._stream.read():
                yield record.data
        else:
            # Incremental reads are not supported
            raise NotImplementedError

    @property
    def name(self) -> str:
        return self._stream.name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._stream.primary_key

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        if self._stream.cursor_field is None:
            return []
        else:
            return self._stream.cursor_field

    @property
    def source_defined_cursor(self) -> bool:
        # Streams must be aware of their cursor at instantiation time
        return True

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        return self._stream.get_json_schema()

    @property
    def supports_incremental(self) -> bool:
        # Only full refresh is supported
        return False

    def check_availability(self, logger: logging.Logger, source: Optional["Source"] = None) -> Tuple[bool, Optional[str]]:
        """
        Verifies the stream is available. Delegates to the underlying AbstractStream and ignores the parameters
        :param logger: (ignored)
        :param source:  (ignored)
        :return:
        """
        return self._stream.check_availability()

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.

        The default implementation of this method does not return user-friendly messages for any exception type, but it should be overriden as needed.

        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error
        """
        return self._stream.get_error_display_message(exception)


class LegacyPartition(Partition):
    """
    This class acts as an adapter between the new Partition interface and the legacy stream_slice "interface"

    LegacyPartitions are instantiated from a Stream and a stream_slice.

    This class can be used to help enable concurrency on existing connectors without having to rewrite everything as AbstractStream.
    In the long-run, it would be preferable to update the connectors, but we don't have the tooling or need to justify the effort at this time.
    """

    def __init__(self, stream: Stream, _slice: Optional[Mapping[str, Any]], message_repository: MessageRepository):
        """
        :param stream: The stream to delegate to
        :param _slice: The partition's stream_slice
        :param message_repository: The message repository to use to emit non-record messages
        """
        self._stream = stream
        self._slice = _slice
        self._message_repository = message_repository

    def read(self) -> Iterable[Record]:
        """
        Read messages from the stream.
        If the StreamData is a Mapping, it will be converted to a Record.
        Otherwise, the message will be emitted on the message repository.
        """
        for record_data in self._stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=copy.deepcopy(self._slice)):
            if isinstance(record_data, Mapping):
                yield Record(record_data)
            else:
                self._message_repository.emit_message(record_data)

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return self._slice

    def __hash__(self) -> int:
        if self._slice:
            # Convert the slice to a string so that it can be hashed
            s = json.dumps(self._slice, sort_keys=True)
            return hash((self._stream.name, s))
        else:
            return hash(self._stream.name)

    def __repr__(self) -> str:
        return f"LegacyPartition({self._stream.name}, {self._slice})"


class LegacyPartitionGenerator(PartitionGenerator):
    """
    This class acts as an adapter between the new PartitionGenerator and Stream.stream_slices

    This class can be used to help enable concurrency on existing connectors without having to rewrite everything as AbstractStream.
    In the long-run, it would be preferable to update the connectors, but we don't have the tooling or need to justify the effort at this time.
    """

    def __init__(self, stream: Stream, message_repository: MessageRepository):
        """
        :param stream: The stream to delegate to
        :param message_repository: The message repository to use to emit non-record messages
        """
        self.message_repository = message_repository
        self._stream = stream

    def generate(self, sync_mode: SyncMode) -> Iterable[Partition]:
        for s in self._stream.stream_slices(sync_mode=sync_mode):
            yield LegacyPartition(self._stream, copy.deepcopy(s), self.message_repository)


@deprecated("This class is experimental. Use at your own risk.")
class LegacyAvailabilityStrategy(AbstractAvailabilityStrategy):
    """
    This class acts as an adapter between the existing AvailabilityStrategy and the new AbstractAvailabilityStrategy.
    LegacyAvailabilityStrategy is instantiated with a Stream and a Source to allow the existing AvailabilityStrategy to be used with the new AbstractAvailabilityStrategy interface.

    A more convenient implementation would not depend on the docs URL instead of the Source itself, and would support running on an AbstractStream instead of only on a Stream.

    This class can be used to help enable concurrency on existing connectors without having to rewrite everything as AbstractStream and AbstractAvailabilityStrategy.
    In the long-run, it would be preferable to update the connectors, but we don't have the tooling or need to justify the effort at this time.
    """

    def __init__(self, stream: Stream, source: Source):
        """
        :param stream: The stream to delegate to
        :param source: The source to delegate to
        """
        self._stream = stream
        self._source = source

    def check_availability(self, logger: logging.Logger) -> Tuple[bool, Optional[str]]:
        return self._stream.check_availability(logger, self._source)


class LegacyErrorMessageParser(ErrorMessageParser):
    """
    This class acts as an adapter between the new ErrorMessageParser interface and the legacy Stream interface

    This class can be used to help enable concurrency on existing connectors without having to rewrite everything as AbstractStream.
    In the long-run, it would be preferable to update the connectors, but we don't have the tooling or need to justify the effort at this time.
    """

    def __init__(self, stream: Stream):
        """
        :param stream: The stream to delegate to
        """
        self._stream = stream

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Always delegate to the stream's get_error_display_message method.
        """
        return self._stream.get_error_display_message(exception)


@deprecated("This class is experimental. Use at your own risk.")
class AvailabilityStrategyFacade(AvailabilityStrategy):
    def __init__(self, abstract_availability_strategy: AbstractAvailabilityStrategy):
        self._abstract_availability_strategy = abstract_availability_strategy

    def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional[Source]) -> Tuple[bool, Optional[str]]:
        """
        Checks stream availability.

        Important to note that the stream and source parameters are not used by the underlying AbstractAvailabilityStrategy.

        :param stream: (unused)
        :param logger: logger object to use
        :param source: (unused)
        :return: A tuple of (boolean, str). If boolean is true, then the stream
        """
        stream_availability = self._abstract_availability_strategy.check_availability(logger)
        return stream_availability.is_available(), stream_availability.message()
