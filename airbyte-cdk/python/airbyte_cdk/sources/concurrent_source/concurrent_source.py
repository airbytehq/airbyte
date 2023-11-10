#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC
from queue import Queue
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.concurrent_source.concurrent_stream_processor import ConcurrentStreamProcessor
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel, QueueItem
from airbyte_cdk.sources.utils.schema_helpers import split_config


class ConcurrentSource(AbstractSource, ABC):
    """
    A Source that reads data from multiple AbstractStreams concurrently.
    It does so by submitting partition generation, and partition read tasks to a thread pool.
    The tasks asynchronously add their output to a shared queue.
    The read is done when all partitions for all streams were generated and read.
    """

    DEFAULT_TIMEOUT_SECONDS = 900

    def __init__(
        self,
        threadpool: ThreadPoolManager,
        message_repository: MessageRepository = InMemoryMessageRepository(),
        max_number_of_partition_generator_in_progress: int = 1,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        **kwargs: Any,
    ) -> None:
        """
        :param threadpool: The threadpool to submit tasks to
        :param message_repository: The repository to emit messages to
        :param max_number_of_partition_generator_in_progress: The maximum number of concurrent partition generation tasks. Limiting this number ensures the source starts reading records instead in a reasonable time instead of generating partitions for all streams first.
        :param timeout_seconds: The maximum number of seconds to wait for a record to be read from the queue. If no record is read within this time, the source will stop reading and return.
        :param kwargs:
        """
        super().__init__(**kwargs)
        self._threadpool = threadpool
        self._message_repository = message_repository
        self._max_number_of_partition_generator_in_progress = max_number_of_partition_generator_in_progress
        self._timeout_seconds = timeout_seconds

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
        config, internal_config = split_config(config)
        stream_name_to_instance: Mapping[str, AbstractStream] = {s.name: s for s in self._streams_as_abstract_streams(config)}

        stream_instances_to_read_from = self._get_streams_to_read_from(catalog, logger, stream_name_to_instance)

        # Return early if there are no streams to read from
        if not stream_instances_to_read_from:
            return

        queue: Queue[QueueItem] = Queue()
        concurrent_stream_processor = ConcurrentStreamProcessor(
            stream_instances_to_read_from,
            PartitionEnqueuer(queue),
            self._threadpool,
            logger,
            self._slice_logger,
            self._message_repository,
            PartitionReader(queue),
        )

        # Enqueue initial partition generation tasks
        yield from self._submit_initial_partition_generators(concurrent_stream_processor)

        # Read from the queue until all partitions were generated and read
        yield from self._consume_from_queue(
            queue,
            concurrent_stream_processor,
        )
        self._threadpool.check_for_errors_and_shutdown()
        self._threadpool.shutdown()
        logger.info(f"Finished syncing {self.name}")

    def _submit_initial_partition_generators(self, concurrent_stream_processor: ConcurrentStreamProcessor) -> Iterable[AirbyteMessage]:
        for _ in range(self._max_number_of_partition_generator_in_progress):
            status_message = concurrent_stream_processor.start_next_partition_generator()
            if status_message:
                yield status_message

    def _consume_from_queue(
        self,
        queue: Queue[QueueItem],
        concurrent_stream_processor: ConcurrentStreamProcessor,
    ) -> Iterable[AirbyteMessage]:
        while airbyte_message_or_record_or_exception := queue.get(block=True, timeout=self._timeout_seconds):
            yield from self._handle_item(
                airbyte_message_or_record_or_exception,
                concurrent_stream_processor,
            )
            if concurrent_stream_processor.is_done() and self._threadpool.is_done() and queue.empty():
                # all partitions were generated and processed. we're done here
                break

    def _handle_item(
        self,
        queue_item: QueueItem,
        concurrent_stream_processor: ConcurrentStreamProcessor,
    ) -> Iterable[AirbyteMessage]:
        # handle queue item and call the appropriate handler depending on the type of the queue item
        if isinstance(queue_item, Exception):
            yield from concurrent_stream_processor.on_exception(queue_item)

        elif isinstance(queue_item, PartitionGenerationCompletedSentinel):
            yield from concurrent_stream_processor.on_partition_generation_completed(queue_item)

        elif isinstance(queue_item, Partition):
            concurrent_stream_processor.on_partition(queue_item)
        elif isinstance(queue_item, PartitionCompleteSentinel):
            yield from concurrent_stream_processor.on_partition_complete_sentinel(queue_item)
        elif isinstance(queue_item, Record):
            # record
            yield from concurrent_stream_processor.on_record(queue_item)
        else:
            raise ValueError(f"Unknown queue item type: {type(queue_item)}")

    def _get_streams_to_read_from(
        self, catalog: ConfiguredAirbyteCatalog, logger: logging.Logger, stream_name_to_instance: Mapping[str, AbstractStream]
    ) -> List[AbstractStream]:
        """
        Iterate over the configured streams and return a list of streams to read from.
        If a stream is not configured, it will be skipped.
        If a stream is configured but does not exist in the source and self.raise_exception_on_missing_stream is True, an exception will be raised
        If a stream is not available, it will be skipped
        """
        stream_instances_to_read_from = []
        for configured_stream in catalog.streams:
            stream_instance = stream_name_to_instance.get(configured_stream.stream.name)
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

    def _streams_as_abstract_streams(self, config: Mapping[str, Any]) -> List[AbstractStream]:
        """
        Ensures the streams are StreamFacade and returns the underlying AbstractStream.
        This is necessary because AbstractSource.streams() returns a List[Stream] and not a List[AbstractStream].
        :param config:
        :return:
        """
        streams = self.streams(config)
        streams_as_abstract_streams = []
        for stream in streams:
            if isinstance(stream, StreamFacade):
                streams_as_abstract_streams.append(stream._abstract_stream)
            else:
                raise ValueError(f"Only StreamFacade is supported by ConcurrentSource. Got {stream}")
        return streams_as_abstract_streams
