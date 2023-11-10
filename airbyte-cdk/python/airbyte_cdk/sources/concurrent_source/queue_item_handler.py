#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import time
from concurrent.futures import Future
from typing import Any, Callable, Dict, Iterable, List, Mapping, Set

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
    TraceType,
)
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message


class QueueItemHandler:
    def __init__(
        self,
        streams_currently_generating_partitions: List[str],
        stream_instances_to_read_from: List[AbstractStream],
        partition_enqueuer: PartitionEnqueuer,
        thread_pool_manager: ThreadPoolManager,
        streams_to_partitions: Dict[str, Set[Partition]],
        record_counter: Dict[str, int],
        stream_to_instance_map: Mapping[str, AbstractStream],
        logger: logging.Logger,
        slice_logger: SliceLogger,
        message_repository: MessageRepository,
        partition_reader: PartitionReader,
    ):
        self._stream_to_instance_map = stream_to_instance_map
        self._record_counter = record_counter
        self._streams_to_partitions = streams_to_partitions
        self._streams_to_partitions = streams_to_partitions
        self._thread_pool_manager = thread_pool_manager
        self._partition_enqueuer = partition_enqueuer
        self._stream_instances_to_read_from = stream_instances_to_read_from
        self._streams_currently_generating_partitions = streams_currently_generating_partitions
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
            ret.append(
                self._start_next_partition_generator(
                    self._stream_instances_to_read_from,
                    self._streams_currently_generating_partitions,
                    self._partition_enqueuer,
                    self._logger,
                )
            )
        return ret

    def on_partition(self, partition: Partition):
        stream_name = partition.stream_name()
        self._streams_to_partitions[stream_name].add(partition)
        if self._slice_logger.should_log_slice_message(self._logger):
            self._message_repository.emit_message(self._slice_logger.create_slice_log_message(partition.to_slice()))
        self._thread_pool_manager.submit(self._partition_reader.process_partition, partition)

    def _is_stream_done(
        self, stream_name: str
    ) -> bool:
        return (
            all([p.is_closed() for p in self._streams_to_partitions[stream_name]]) and stream_name not in self._streams_currently_generating_partitions
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

    def _start_next_partition_generator(
        self,
        streams: List[AbstractStream],
        streams_currently_generating_partitions: List[str],
        partition_enqueuer: PartitionEnqueuer,
        logger: logging.Logger,
    ) -> AirbyteMessage:
        stream = streams.pop(0)
        self._thread_pool_manager.submit(partition_enqueuer.generate_partitions, stream)
        streams_currently_generating_partitions.append(stream.name)
        logger.info(f"Marking stream {stream.name} as STARTED")
        logger.info(f"Syncing stream: {stream.name} ")
        return stream_status_as_airbyte_message(
            stream.as_airbyte_stream(),
            AirbyteStreamStatus.STARTED,
        )
