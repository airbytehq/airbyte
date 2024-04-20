#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent
import logging
from queue import Queue
from typing import Iterable, Iterator, List

from airbyte_cdk.models import AirbyteMessage
from airbyte_cdk.sources.concurrent_source.concurrent_read_processor import ConcurrentReadProcessor
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.stream_thread_exception import StreamThreadException
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel, QueueItem
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger, SliceLogger


class ConcurrentSource:
    """
    A Source that reads data from multiple AbstractStreams concurrently.
    It does so by submitting partition generation, and partition read tasks to a thread pool.
    The tasks asynchronously add their output to a shared queue.
    The read is done when all partitions for all streams w ere generated and read.
    """

    DEFAULT_TIMEOUT_SECONDS = 900

    @staticmethod
    def create(
        num_workers: int,
        initial_number_of_partitions_to_generate: int,
        logger: logging.Logger,
        slice_logger: SliceLogger,
        message_repository: MessageRepository,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> "ConcurrentSource":
        is_single_threaded = initial_number_of_partitions_to_generate == 1 and num_workers == 1
        too_many_generator = not is_single_threaded and initial_number_of_partitions_to_generate >= num_workers
        assert not too_many_generator, "It is required to have more workers than threads generating partitions"
        threadpool = ThreadPoolManager(
            concurrent.futures.ThreadPoolExecutor(max_workers=num_workers, thread_name_prefix="workerpool"),
            logger,
        )
        return ConcurrentSource(
            threadpool, logger, slice_logger, message_repository, initial_number_of_partitions_to_generate, timeout_seconds
        )

    def __init__(
        self,
        threadpool: ThreadPoolManager,
        logger: logging.Logger,
        slice_logger: SliceLogger = DebugSliceLogger(),
        message_repository: MessageRepository = InMemoryMessageRepository(),
        initial_number_partitions_to_generate: int = 1,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """
        :param threadpool: The threadpool to submit tasks to
        :param logger: The logger to log to
        :param slice_logger: The slice logger used to create messages on new slices
        :param message_repository: The repository to emit messages to
        :param initial_number_partitions_to_generate: The initial number of concurrent partition generation tasks. Limiting this number ensures will limit the latency of the first records emitted. While the latency is not critical, emitting the records early allows the platform and the destination to process them as early as possible.
        :param timeout_seconds: The maximum number of seconds to wait for a record to be read from the queue. If no record is read within this time, the source will stop reading and return.
        """
        self._threadpool = threadpool
        self._logger = logger
        self._slice_logger = slice_logger
        self._message_repository = message_repository
        self._initial_number_partitions_to_generate = initial_number_partitions_to_generate
        self._timeout_seconds = timeout_seconds

    def read(
        self,
        streams: List[AbstractStream],
    ) -> Iterator[AirbyteMessage]:
        self._logger.info("Starting syncing")
        stream_instances_to_read_from = self._get_streams_to_read_from(streams)

        # Return early if there are no streams to read from
        if not stream_instances_to_read_from:
            return

        # We set a maxsize to for the main thread to process record items when the queue size grows. This assumes that there are less
        # threads generating partitions that than are max number of workers. If it weren't the case, we could have threads only generating
        # partitions which would fill the queue. This number is arbitrarily set to 10_000 but will probably need to be changed given more
        # information and might even need to be configurable depending on the source
        queue: Queue[QueueItem] = Queue(maxsize=10_000)
        concurrent_stream_processor = ConcurrentReadProcessor(
            stream_instances_to_read_from,
            PartitionEnqueuer(queue, self._threadpool),
            self._threadpool,
            self._logger,
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
        self._logger.info("Finished syncing")

    def _submit_initial_partition_generators(self, concurrent_stream_processor: ConcurrentReadProcessor) -> Iterable[AirbyteMessage]:
        for _ in range(self._initial_number_partitions_to_generate):
            status_message = concurrent_stream_processor.start_next_partition_generator()
            if status_message:
                yield status_message

    def _consume_from_queue(
        self,
        queue: Queue[QueueItem],
        concurrent_stream_processor: ConcurrentReadProcessor,
    ) -> Iterable[AirbyteMessage]:
        while airbyte_message_or_record_or_exception := queue.get():
            yield from self._handle_item(
                airbyte_message_or_record_or_exception,
                concurrent_stream_processor,
            )
            if concurrent_stream_processor.is_done() and queue.empty():
                # all partitions were generated and processed. we're done here
                break

    def _handle_item(
        self,
        queue_item: QueueItem,
        concurrent_stream_processor: ConcurrentReadProcessor,
    ) -> Iterable[AirbyteMessage]:
        # handle queue item and call the appropriate handler depending on the type of the queue item
        if isinstance(queue_item, StreamThreadException):
            yield from concurrent_stream_processor.on_exception(queue_item)
        elif isinstance(queue_item, PartitionGenerationCompletedSentinel):
            yield from concurrent_stream_processor.on_partition_generation_completed(queue_item)
        elif isinstance(queue_item, Partition):
            concurrent_stream_processor.on_partition(queue_item)
        elif isinstance(queue_item, PartitionCompleteSentinel):
            yield from concurrent_stream_processor.on_partition_complete_sentinel(queue_item)
        elif isinstance(queue_item, Record):
            yield from concurrent_stream_processor.on_record(queue_item)
        else:
            raise ValueError(f"Unknown queue item type: {type(queue_item)}")

    def _get_streams_to_read_from(self, streams: List[AbstractStream]) -> List[AbstractStream]:
        """
        Iterate over the configured streams and return a list of streams to read from.
        If a stream is not configured, it will be skipped.
        If a stream is configured but does not exist in the source and self.raise_exception_on_missing_stream is True, an exception will be raised
        If a stream is not available, it will be skipped
        """
        stream_instances_to_read_from = []
        for stream in streams:
            stream_availability = stream.check_availability()
            if not stream_availability.is_available():
                self._logger.warning(f"Skipped syncing stream '{stream.name}' because it was unavailable. {stream_availability.message()}")
                continue
            stream_instances_to_read_from.append(stream)
        return stream_instances_to_read_from
