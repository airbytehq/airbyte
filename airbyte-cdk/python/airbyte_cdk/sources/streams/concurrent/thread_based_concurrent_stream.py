#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent
import time
from concurrent.futures import Future
from functools import lru_cache
from logging import Logger
from queue import Queue
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional

from airbyte_cdk.models import AirbyteStream, SyncMode
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import AbstractAvailabilityStrategy, StreamAvailability
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor, NoopCursor
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PARTITIONS_GENERATED_SENTINEL, PartitionCompleteSentinel, QueueItem
from airbyte_cdk.sources.utils.slice_logger import SliceLogger


class ThreadBasedConcurrentStream(AbstractStream):

    DEFAULT_TIMEOUT_SECONDS = 900
    DEFAULT_MAX_QUEUE_SIZE = 10_000
    DEFAULT_SLEEP_TIME = 0.1

    def __init__(
        self,
        partition_generator: PartitionGenerator,
        max_workers: int,
        name: str,
        json_schema: Mapping[str, Any],
        availability_strategy: AbstractAvailabilityStrategy,
        primary_key: List[str],
        cursor_field: Optional[str],
        slice_logger: SliceLogger,
        logger: Logger,
        message_repository: MessageRepository,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        max_concurrent_tasks: int = DEFAULT_MAX_QUEUE_SIZE,
        sleep_time: float = DEFAULT_SLEEP_TIME,
        cursor: Cursor = NoopCursor(),
        namespace: Optional[str] = None,
    ):
        self._stream_partition_generator = partition_generator
        self._max_workers = max_workers
        self._threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool")
        self._name = name
        self._json_schema = json_schema
        self._availability_strategy = availability_strategy
        self._primary_key = primary_key
        self._cursor_field = cursor_field
        self._slice_logger = slice_logger
        self._logger = logger
        self._message_repository = message_repository
        self._timeout_seconds = timeout_seconds
        self._max_concurrent_tasks = max_concurrent_tasks
        self._sleep_time = sleep_time
        self._cursor = cursor
        self._namespace = namespace

    def read(self) -> Iterable[Record]:
        """
        Read all data from the stream (only full-refresh is supported at the moment)

        Algorithm:
        1. Submit a future to generate the stream's partition to process.
          - This has to be done asynchronously because we sometimes need to submit requests to the API to generate all partitions (eg for substreams).
          - The future will add the partitions to process on a work queue.
        2. Continuously poll work from the work queue until all partitions are generated and processed
          - If the next work item is an Exception, stop the threadpool and raise it.
          - If the next work item is a partition, submit a future to process it.
            - The future will add the records to emit on the work queue.
            - Add the partitions to the partitions_to_done dict so we know it needs to complete for the sync to succeed.
          - If the next work item is a record, yield the record.
          - If the next work item is PARTITIONS_GENERATED_SENTINEL, all the partitions were generated.
          - If the next work item is a PartitionCompleteSentinel, a partition is done processing.
            - Update the value in partitions_to_done to True so we know the partition is completed.
        """
        self._logger.debug(f"Processing stream slices for {self.name}")
        futures: List[Future[Any]] = []
        queue: Queue[QueueItem] = Queue()
        partition_generator = PartitionEnqueuer(queue, PARTITIONS_GENERATED_SENTINEL)
        partition_reader = PartitionReader(queue)

        self._submit_task(futures, partition_generator.generate_partitions, self._stream_partition_generator)

        # True -> partition is done
        # False -> partition is not done
        partitions_to_done: Dict[Partition, bool] = {}

        finished_partitions = False
        while record_or_partition_or_exception := queue.get(block=True, timeout=self._timeout_seconds):
            if isinstance(record_or_partition_or_exception, Exception):
                # An exception was raised while processing the stream
                # Stop the threadpool and raise it
                self._stop_and_raise_exception(record_or_partition_or_exception)
            elif record_or_partition_or_exception == PARTITIONS_GENERATED_SENTINEL:
                # All partitions were generated
                finished_partitions = True
            elif isinstance(record_or_partition_or_exception, PartitionCompleteSentinel):
                # All records for a partition were generated
                if record_or_partition_or_exception.partition not in partitions_to_done:
                    raise RuntimeError(
                        f"Received sentinel for partition {record_or_partition_or_exception.partition} that was not in partitions. This is indicative of a bug in the CDK. Please contact support.partitions:\n{partitions_to_done}"
                    )
                partitions_to_done[record_or_partition_or_exception.partition] = True
                self._cursor.close_partition(record_or_partition_or_exception.partition)
            elif isinstance(record_or_partition_or_exception, Record):
                # Emit records
                yield record_or_partition_or_exception
                self._cursor.observe(record_or_partition_or_exception)
            elif isinstance(record_or_partition_or_exception, Partition):
                # A new partition was generated and must be processed
                partitions_to_done[record_or_partition_or_exception] = False
                if self._slice_logger.should_log_slice_message(self._logger):
                    self._message_repository.emit_message(
                        self._slice_logger.create_slice_log_message(record_or_partition_or_exception.to_slice())
                    )
                self._submit_task(futures, partition_reader.process_partition, record_or_partition_or_exception)
            if finished_partitions and all(partitions_to_done.values()):
                # All partitions were generated and process. We're done here
                break
        self._check_for_errors(futures)

    def _submit_task(self, futures: List[Future[Any]], function: Callable[..., Any], *args: Any) -> None:
        # Submit a task to the threadpool, waiting if there are too many pending tasks
        self._wait_while_too_many_pending_futures(futures)
        futures.append(self._threadpool.submit(function, *args))

    def _wait_while_too_many_pending_futures(self, futures: List[Future[Any]]) -> None:
        # Wait until the number of pending tasks is < self._max_concurrent_tasks
        while True:
            pending_futures = [f for f in futures if not f.done()]
            if len(pending_futures) < self._max_concurrent_tasks:
                break
            self._logger.info("Main thread is sleeping because the task queue is full...")
            time.sleep(self._sleep_time)

    def _check_for_errors(self, futures: List[Future[Any]]) -> None:
        exceptions_from_futures = [f for f in [future.exception() for future in futures] if f is not None]
        if exceptions_from_futures:
            exception = RuntimeError(f"Failed reading from stream {self.name} with errors: {exceptions_from_futures}")
            self._stop_and_raise_exception(exception)
        else:
            futures_not_done = [f for f in futures if not f.done()]
            if futures_not_done:
                exception = RuntimeError(f"Failed reading from stream {self.name} with futures not done: {futures_not_done}")
                self._stop_and_raise_exception(exception)

    def _stop_and_raise_exception(self, exception: BaseException) -> None:
        self._threadpool.shutdown(wait=False, cancel_futures=True)
        raise exception

    @property
    def name(self) -> str:
        return self._name

    def check_availability(self) -> StreamAvailability:
        return self._availability_strategy.check_availability(self._logger)

    @property
    def cursor_field(self) -> Optional[str]:
        return self._cursor_field

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        return self._json_schema

    def as_airbyte_stream(self) -> AirbyteStream:
        stream = AirbyteStream(name=self.name, json_schema=dict(self._json_schema), supported_sync_modes=[SyncMode.full_refresh])

        if self._namespace:
            stream.namespace = self._namespace

        if self._cursor_field:
            stream.source_defined_cursor = True
            stream.supported_sync_modes.append(SyncMode.incremental)
            stream.default_cursor_field = [self._cursor_field]

        keys = self._primary_key
        if keys and len(keys) > 0:
            stream.source_defined_primary_key = [keys]

        return stream

    def log_stream_sync_configuration(self) -> None:
        self._logger.debug(
            f"Syncing stream instance: {self.name}",
            extra={
                "primary_key": self._primary_key,
                "cursor_field": self.cursor_field,
            },
        )
