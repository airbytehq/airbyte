#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Set, Union

from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, AirbyteStreamStatus, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.queue_item_handler import QueueItemHandler
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel, QueueItem
from airbyte_cdk.sources.utils.schema_helpers import split_config
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message


class Status(Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


@dataclass
class PartitionReadStatus:
    partition: Partition
    partition_read_status: Status


@dataclass
class StreamReadStatus:
    stream: AbstractStream
    partition_generation_status: Status
    partition_read_statuses: List[PartitionReadStatus]


class ConcurrentSource(AbstractSource, ABC):
    def __init__(
        self,
        threadpool: ThreadPoolManager,
        message_repository: MessageRepository = InMemoryMessageRepository(),
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._threadpool = threadpool
        assert isinstance(threadpool, ThreadPoolManager)
        self._message_repository = message_repository

    @property
    def message_repository(self) -> MessageRepository:
        return self._message_repository

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[Union[List[AirbyteStateMessage], MutableMapping[str, Any]]] = None,
    ) -> Iterator[AirbyteMessage]:
        logger.info(f"Starting syncing {self.name}")
        queue: Queue[QueueItem] = Queue()
        partition_enqueuer = PartitionEnqueuer(queue)
        config, internal_config = split_config(config)
        stream_to_instance_map: Mapping[str, AbstractStream] = {s.name: s for s in self._streams_as_abstract_streams(config)}

        # FIXME
        max_number_of_partition_generator_in_progress = max(1, 1)

        stream_instances_to_read_from = self._get_streams_to_read_from(catalog, logger, stream_to_instance_map)
        streams_currently_generating_partitions: List[str] = []
        streams_to_partitions: Dict[str, Set[Partition]] = {}
        record_counter = {}
        for stream in stream_instances_to_read_from:
            streams_to_partitions[stream.name] = set()
            record_counter[stream.name] = 0
        if not stream_instances_to_read_from:
            return
        while len(streams_currently_generating_partitions) < max_number_of_partition_generator_in_progress:
            yield self._start_next_partition_generator(
                stream_instances_to_read_from,
                streams_currently_generating_partitions,
                partition_enqueuer,
                logger,
            )
        partition_reader = PartitionReader(queue)
        queue_item_handler = QueueItemHandler(
            streams_currently_generating_partitions,
            stream_instances_to_read_from,
            partition_enqueuer,
            self._threadpool,
            streams_to_partitions,
            record_counter,
            stream_to_instance_map,
            logger,
            self._slice_logger,
            self._message_repository,
            partition_reader,
        )
        yield from self._consume_from_queue(
            queue,
            streams_to_partitions,
            streams_currently_generating_partitions,
            stream_instances_to_read_from,
            queue_item_handler,
        )
        self._threadpool.check_for_errors_and_shutdown()
        self._threadpool.shutdown()
        logger.info(f"Finished syncing {self.name}")

    def _consume_from_queue(
        self,
        queue: Queue[QueueItem],
        streams_to_partitions: Dict[str, Set[Partition]],
        streams_currently_generating_partitions: List[str],
        stream_instances_to_read_from: List[AbstractStream],
        queue_item_handler: QueueItemHandler,
    ) -> Iterable[AirbyteMessage]:
        # FIXME
        while airbyte_message_or_record_or_exception := queue.get(block=True, timeout=300):
            yield from self._handle_item(
                airbyte_message_or_record_or_exception,
                queue_item_handler,
            )
            if self._is_done(streams_to_partitions, stream_instances_to_read_from, streams_currently_generating_partitions):
                # all partitions were generated and process. we're done here
                if self._threadpool.is_done() and queue.empty():
                    break

    def _handle_item(
        self,
        queue_item: QueueItem,
        queue_item_handler: QueueItemHandler,
    ) -> Iterable[AirbyteMessage]:
        if isinstance(queue_item, Exception):
            yield from queue_item_handler.on_exception(queue_item)

        elif isinstance(queue_item, PartitionGenerationCompletedSentinel):
            yield from queue_item_handler.on_partition_generation_completed(queue_item)

        elif isinstance(queue_item, Partition):
            # a new partition was generated and must be processed
            queue_item_handler.on_partition(queue_item)
        elif isinstance(queue_item, PartitionCompleteSentinel):
            yield from queue_item_handler.on_partition_complete_sentinel(queue_item)
        else:
            # record
            yield from queue_item_handler.on_record(queue_item)

    def _get_streams_to_read_from(
        self, catalog: ConfiguredAirbyteCatalog, logger: logging.Logger, stream_to_instance_map: Mapping[str, AbstractStream]
    ) -> List[AbstractStream]:
        stream_instances_to_read_from = []
        for configured_stream in catalog.streams:
            stream_instance = stream_to_instance_map.get(configured_stream.stream.name)
            if not stream_instance:
                if not self.raise_exception_on_missing_stream:
                    continue
                raise KeyError(
                    f"The stream {configured_stream.stream.name} no longer exists in the configuration. "
                    f"Refresh the schema in replication settings and remove this stream from future sync attempts."
                )
            else:
                stream_availability = stream_instance.check_availability()
                if not stream_availability.is_available():
                    logger.warning(
                        f"Skipped syncing stream '{stream_instance.name}' because it was unavailable. {stream_availability.message()}"
                    )
                    continue
                stream_instances_to_read_from.append(stream_instance)
        return stream_instances_to_read_from

    def _is_done(
        self,
        streams_to_partitions: Dict[str, Set[Partition]],
        stream_instances_to_read_from: List[AbstractStream],
        streams_currently_generating_partitions: List[str],
    ) -> bool:
        return (
            not streams_currently_generating_partitions
            and not stream_instances_to_read_from
            and all([all(p.is_closed() for p in partitions) for partitions in streams_to_partitions.values()])
        )

    def _start_next_partition_generator(
        self,
        streams: List[AbstractStream],
        streams_currently_generating_partitions: List[str],
        partition_enqueuer: PartitionEnqueuer,
        logger: logging.Logger,
    ) -> AirbyteMessage:
        stream = streams.pop(0)
        self._threadpool.submit(partition_enqueuer.generate_partitions, stream)
        streams_currently_generating_partitions.append(stream.name)
        logger.info(f"Marking stream {stream.name} as STARTED")
        logger.info(f"Syncing stream: {stream.name} ")
        return stream_status_as_airbyte_message(
            stream.as_airbyte_stream(),
            AirbyteStreamStatus.STARTED,
        )

    def _streams_as_abstract_streams(self, config: Mapping[str, Any]) -> List[AbstractStream]:
        streams = self.streams(config)
        streams_as_abstract_streams = []
        for stream in streams:
            if isinstance(stream, StreamFacade):
                streams_as_abstract_streams.append(stream._abstract_stream)
            else:
                raise ValueError(f"Only StreamFacade is supported by ConcurrentSource. Got {stream}")
        return streams_as_abstract_streams
