#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
import logging
import threading
from queue import Queue
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource

# from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams import Stream

# from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
# from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.adapters import (
    StreamAvailabilityStrategy,
    StreamFacade,
    StreamPartition,
    StreamPartitionGenerator,
)

# from airbyte_cdk.sources.streams.concurrent.availability_strategy import (
#     AbstractAvailabilityStrategy,
#     StreamAvailability,
#     StreamAvailable,
#     StreamUnavailable,
# )
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor, NoopCursor
from airbyte_cdk.sources.streams.concurrent.exceptions import ExceptionWithDisplayMessage
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition

# from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel, QueueItem
from airbyte_cdk.sources.streams.concurrent.thread_based_concurrent_stream import ThreadBasedConcurrentStream

# from airbyte_cdk.sources.streams.core import StreamData
# from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
# from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from deprecated.classic import deprecated

thread_local = threading.local()

"""
This module contains adapters to help enabling concurrency on File-based Stream objects without needing to migrate to AbstractStream
"""


@deprecated("This class is experimental. Use at your own risk.")
class FileBasedStreamFacade(StreamFacade):
    """
    The FileBasedStreamFacade is a Stream that wraps an AbstractFileBasedStream and exposes it as a Stream.

    All methods either delegate to the wrapped AbstractStream or provide a default implementation.
    The default implementations define restrictions imposed on Streams migrated to the new interface. For instance, only source-defined cursors are supported.
    """

    @classmethod
    def create_from_stream(
        cls,
        stream: AbstractFileBasedStream,
        source: AbstractSource,
        logger: logging.Logger,
        max_workers: int,
        state: Optional[MutableMapping[str, Any]],
        cursor: Cursor,
    ) -> Stream:
        """
        Create a ConcurrentStream from a FileBasedStream object.
        :param source: The source
        :param stream: The stream
        :param max_workers: The maximum number of worker thread to use
        :return:
        """
        pk = cls._get_primary_key_from_stream(stream.primary_key)
        cursor_field = cls._get_cursor_field_from_stream(stream)

        if not source.message_repository:
            raise ValueError(
                "A message repository is required to emit non-record messages. Please set the message repository on the source."
            )

        message_repository = source.message_repository
        return StreamFacade(
            ThreadBasedConcurrentStream(
                partition_generator=StreamPartitionGenerator(
                    stream,
                    message_repository,
                    SyncMode.full_refresh if isinstance(cursor, NoopCursor) else SyncMode.incremental,
                    [cursor_field] if cursor_field is not None else None,
                    state,
                ),
                max_workers=max_workers,
                name=stream.name,
                namespace=stream.namespace,
                json_schema=stream.get_json_schema(),
                availability_strategy=StreamAvailabilityStrategy(stream, source),
                primary_key=pk,
                cursor_field=cursor_field,
                slice_logger=source._slice_logger,
                message_repository=message_repository,
                logger=logger,
                cursor=cursor,
            ),
            stream,
            cursor,
        )


class FileBasedStreamPartition(StreamPartition):
    """
    This class acts as an adapter between the new Partition interface and the FileBasedStream's stream_slice interface

    FileBasedStreamPartition are instantiated from a Stream and a stream_slice.

    This class can be used to help enable concurrency on existing connectors without having to rewrite everything as AbstractStream.
    In the long-run, it would be preferable to update the connectors, but we don't have the tooling or need to justify the effort at this time.
    """

    _reader_pool: Iterator[AbstractFileBasedStreamReader] = []
    readers: MutableMapping[str, AbstractFileBasedStreamReader] = {}

    def __init__(
        self,
        stream: AbstractFileBasedStream,
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

    @classmethod
    def set_reader_pool(cls, readers: List[AbstractFileBasedStreamReader]):
        if not cls._reader_pool:
            cls._reader_pool = readers
        else:
            raise AssertionError("set_reader_pool should only be called once")

    def read(self) -> Iterable[Record]:
        """
        Read messages from the stream.
        If the StreamData is a Mapping, it will be converted to a Record.
        Otherwise, the message will be emitted on the message repository.
        """
        try:
            thread_id = self.get_thread_id()
            if thread_id not in self.readers:
                try:
                    self.readers[thread_id] = next(self._reader_pool)
                except StopIteration:
                    raise AssertionError(
                        "Ran out of readers for the threadpool. This means that there are more threads than readers; this should never happen because threads and readers should be 1:1."
                    )
            stream_reader = self.readers[thread_id]

            # using `stream_state=self._state` have a very different behavior than the current one as today the state is updated slice
            #  by slice incrementally. We don't have this guarantee with Concurrent CDK. For HttpStream, `stream_state` is passed to:
            #  * fetch_next_page
            #  * parse_response
            #  Both are not used for Stripe so we should be good for the first iteration of Concurrent CDK. However, Stripe still do
            #  `if not stream_state` to know if it calls the Event stream or not
            for record_data in self._stream.read_records_from_slice(
                stream_slice=copy.deepcopy(self._slice),
                stream_reader=stream_reader,
            ):
                if isinstance(record_data, Mapping):
                    data_to_return = dict(record_data)
                    self._stream.transformer.transform(data_to_return, self._stream.get_json_schema())
                    yield Record(data_to_return)
                else:
                    self._message_repository.emit_message(record_data)
        except Exception as e:
            display_message = self._stream.get_error_display_message(e)
            if display_message:
                raise ExceptionWithDisplayMessage(display_message) from e
            else:
                raise e

    def to_slice(self) -> Optional[Mapping[str, Any]]:
        return {"_ab_source_file_last_modified": f"{self._slice['files'][0].last_modified}_{self._slice['files'][0].uri}"}

    def __hash__(self) -> int:
        if self._slice:
            # Convert the slice to a string so that it can be hashed
            if len(self._slice["files"]) != 1:
                raise ValueError(f"THIS SHOULDN'T BE != 1!! {self._slice['files']}")
            else:
                s = json.dumps(f"{self._slice['files'][0].last_modified}_{self._slice['files'][0].uri}")
            return hash((self._stream.name, s))
        else:
            return hash(self._stream.name)

    def __repr__(self) -> str:
        return f"StreamPartition({self._stream.name}, {self._slice})"


class StreamReaderPool:
    def __init__(self, stream_readers):
        self.stream_readers = Queue(len(stream_readers))
        for stream_reader in stream_readers:
            self.stream_readers.put(stream_reader)

    def get_stream_reader(self):
        return self.stream_readers.get()

    def return_stream_reader(self, connection):
        self.stream_readers.put(connection)


class FileBasedStreamPartitionReader:
    """
    Generates records from a partition and puts them in a queue.
    """

    def __init__(self, queue: Queue[QueueItem], stream_reader_pool: StreamReaderPool) -> None:
        """
        :param queue: The queue to put the records in.
        """
        self._queue = queue
        self._stream_reader_pool = stream_reader_pool

    # def _get_stream_reader(self) -> AbstractFileBasedStreamReader:
    #     if not hasattr(thread_local, "stream_reader"):
    #         thread_local.stream_reader = make_stream_reader()
    #
    #     if not hasattr(thread_local, "stream_reader"):
    #         self._set_stream_reader(self._stream_reader_pool.get_stream_reader())
    #     return thread_local.stream_reader

    def _set_stream_reader(self, stream_reader: AbstractFileBasedStreamReader) -> None:
        thread_local.stream_reader = stream_reader

    def process_partition(self, partition: Partition) -> None:
        """
        Process a partition and put the records in the output queue.
        When all the partitions are added to the queue, a sentinel is added to the queue to indicate that all the partitions have been generated.

        If an exception is encountered, the exception will be caught and put in the queue.

        This method is meant to be called from a thread.
        :param partition: The partition to read data from
        :return: None
        """
        partition.stream_reader = self._get_stream_reader()
        try:
            for record in partition.read():
                self._queue.put(record)
            self._queue.put(PartitionCompleteSentinel(partition))
        except Exception as e:
            self._queue.put(e)
        finally:
            self._stream_reader_pool.return_stream_reader(thread_local.stream_reader)
            del thread_local.stream_reader
