#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Iterable, List, Mapping, Optional

from airbyte_cdk.models import AirbyteMessage, AirbyteStreamStatus
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message


class ConcurrentStreamProcessor:
    def __init__(
        self,
        stream_instances_to_read_from: List[AbstractStream],
        partition_enqueuer: PartitionEnqueuer,
        thread_pool_manager: ThreadPoolManager,
        stream_to_instance_map: Mapping[str, AbstractStream],
        logger: logging.Logger,
        slice_logger: SliceLogger,
        message_repository: MessageRepository,
        partition_reader: PartitionReader,
    ):
        """
        This class is responsible for handling items from a concurrent stream read process.
        :param stream_instances_to_read_from:
        :param partition_enqueuer:
        :param thread_pool_manager:
        :param stream_to_instance_map:
        :param logger:
        :param slice_logger:
        :param message_repository:
        :param partition_reader:
        """
        self._stream_to_instance_map = stream_to_instance_map
        self._record_counter = {}
        self._streams_to_partitions = {}
        for stream in stream_instances_to_read_from:
            self._streams_to_partitions[stream.name] = set()
            self._record_counter[stream.name] = 0
        self._thread_pool_manager = thread_pool_manager
        self._partition_enqueuer = partition_enqueuer
        self._stream_instances_to_read_from = stream_instances_to_read_from
        self._streams_currently_generating_partitions = []
        self._logger = logger
        self._slice_logger = slice_logger
        self._message_repository = message_repository
        self._partition_reader = partition_reader

    def on_partition_generation_completed(self, sentinel: PartitionGenerationCompletedSentinel) -> Iterable[AirbyteMessage]:
        stream_name = sentinel.stream.name
        self._streams_currently_generating_partitions.remove(sentinel.stream.name)
        ret = []
        if self._is_stream_done(stream_name):
            ret.append(self._on_stream_is_done(stream_name))
        if self._stream_instances_to_read_from:
            ret.append(self.start_next_partition_generator())
        return ret

    def on_partition(self, partition: Partition) -> None:
        stream_name = partition.stream_name()
        self._streams_to_partitions[stream_name].add(partition)
        if self._slice_logger.should_log_slice_message(self._logger):
            self._message_repository.emit_message(self._slice_logger.create_slice_log_message(partition.to_slice()))
        self._thread_pool_manager.submit(self._partition_reader.process_partition, partition)

    def _is_stream_done(self, stream_name: str) -> bool:
        return (
            all([p.is_closed() for p in self._streams_to_partitions[stream_name]])
            and stream_name not in self._streams_currently_generating_partitions
        )

    def _on_stream_is_done(self, stream_name: str) -> AirbyteMessage:
        self._logger.info(f"Read {self._record_counter[stream_name]} records from {stream_name} stream")
        self._logger.info(f"Marking stream {stream_name} as STOPPED")
        stream = self._stream_to_instance_map[stream_name]
        self._logger.info(f"Finished syncing {stream.name}")
        return stream_status_as_airbyte_message(stream.as_airbyte_stream(), AirbyteStreamStatus.COMPLETE)

    def on_partition_complete_sentinel(self, sentinel: PartitionCompleteSentinel) -> Iterable[AirbyteMessage]:
        # all records for a partition were generated
        partition = sentinel.partition
        partition.close()
        if self._is_stream_done(partition.stream_name()):
            yield self._on_stream_is_done(partition.stream_name())
        yield from self._message_repository.consume_queue()

    def on_record(self, record: Record) -> Iterable[AirbyteMessage]:
        # Do not pass a transformer or a schema
        # AbstractStreams are expected to return data as they are expected.
        # Any transformation on the data should be done before reaching this point
        message = stream_data_to_airbyte_message(record.stream_name, record.data)
        stream = self._stream_to_instance_map[record.stream_name]

        if self._record_counter[stream.name] == 0:
            self._logger.info(f"Marking stream {stream.name} as RUNNING")
            yield stream_status_as_airbyte_message(stream.as_airbyte_stream(), AirbyteStreamStatus.RUNNING)

        if message.type == MessageType.RECORD:
            self._record_counter[stream.name] += 1
        yield message
        yield from self._message_repository.consume_queue()

    def on_exception(self, exception: Exception) -> Iterable[AirbyteMessage]:
        yield from self._stop_streams()
        raise exception

    def _stop_streams(self) -> Iterable[AirbyteMessage]:
        self._thread_pool_manager.shutdown()
        for stream_name, partitions in self._streams_to_partitions.items():
            stream = self._stream_to_instance_map[stream_name]
            if not all([p.is_closed() for p in partitions]):
                self._logger.info(f"Marking stream {stream.name} as STOPPED")
                self._logger.info(f"Finished syncing {stream.name}")
                yield stream_status_as_airbyte_message(stream.as_airbyte_stream(), AirbyteStreamStatus.INCOMPLETE)

    def start_next_partition_generator(self) -> Optional[AirbyteMessage]:
        if self._stream_instances_to_read_from:
            stream = self._stream_instances_to_read_from.pop(0)
            self._thread_pool_manager.submit(self._partition_enqueuer.generate_partitions, stream)
            self._streams_currently_generating_partitions.append(stream.name)
            self._logger.info(f"Marking stream {stream.name} as STARTED")
            self._logger.info(f"Syncing stream: {stream.name} ")
            return stream_status_as_airbyte_message(
                stream.as_airbyte_stream(),
                AirbyteStreamStatus.STARTED,
            )
        else:
            return None

    def is_done(self) -> bool:
        return (
            not self._streams_currently_generating_partitions
            and not self._stream_instances_to_read_from
            and all([all(p.is_closed() for p in partitions) for partitions in self._streams_to_partitions.values()])
        )
