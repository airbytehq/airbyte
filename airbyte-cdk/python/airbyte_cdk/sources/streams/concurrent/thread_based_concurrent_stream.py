#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent
from concurrent.futures import Future
from functools import lru_cache
from queue import Queue
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream, FieldPath
from airbyte_cdk.sources.streams.concurrent.availability_strategy import AbstractAvailabilityStrategy
from airbyte_cdk.sources.streams.concurrent.error_message_parser import ErrorMessageParser
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PARTITIONS_GENERATED_SENTINEL, PartitionCompleteSentinel, QueueItem
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.slice_logger import SliceLogger


class ThreadBasedConcurrentStream(AbstractStream):

    TIMEOUT_SECONDS = 300

    def __init__(
        self,
        partition_generator: PartitionGenerator,
        max_workers: int,
        name: str,
        json_schema: Mapping[str, Any],
        availability_strategy: AbstractAvailabilityStrategy,
        primary_key: Optional[FieldPath],
        cursor_field: Union[str, List[str]],
        error_display_message_parser: ErrorMessageParser,
        slice_logger: SliceLogger,
    ):
        self._stream_partition_generator = partition_generator
        self._max_workers = max_workers
        self._threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool")
        self._name = name
        self._json_schema = json_schema
        self._availability_strategy = availability_strategy
        self._primary_key = primary_key
        self._cursor_field = cursor_field
        self._error_message_parser = error_display_message_parser
        self._slice_logger = slice_logger

    def read(self) -> Iterable[StreamData]:
        """
        Read all data from the stream (only full-refresh is supported at the moment)

        Algorithm:
        1. Submit a future to generate the stream's partition to process.
          - This has to be done asynchronously because we sometimes need to submit requests to the API to generate all partitions (eg for substreams).
          - The future will add the partitions to process on a work queue
        2. Continuously poll work from the work queue until all partitions are generated and processed
          - If the next work item is a partition, submit a future to process it.
            - The future will add the records to emit on the work queue
            - Add the partitions to the partitions_to_done dict so we know it needs to complete for the sync to succeed
          - If the next work item is a record, yield the record
          - If the next work item is PARTITIONS_GENERATED_SENTINEL, all the partitions were generated
          - If the next work item is a PartitionCompleteSentinel, a partition is done processing
            - Update the value in partitions_to_done to True so we know the partition is completed
        """
        self.logger.debug(f"Processing stream slices for {self.name} (sync_mode: full_refresh)")
        futures = []
        queue: Queue[QueueItem] = Queue()
        partition_generator = PartitionEnqueuer(queue, PARTITIONS_GENERATED_SENTINEL)
        partition_reader = PartitionReader(queue)

        # Submit partition generation tasks
        futures.append(
            self._threadpool.submit(partition_generator.generate_partitions, self._stream_partition_generator, SyncMode.full_refresh)
        )

        # True -> partition is done
        # False -> partition is not done
        partitions_to_done: Dict[Partition, bool] = {}

        finished_partitions = False
        while record_or_partition := queue.get(block=True, timeout=self.TIMEOUT_SECONDS):
            if record_or_partition == PARTITIONS_GENERATED_SENTINEL:
                # All partitions were generated
                finished_partitions = True
            elif isinstance(record_or_partition, PartitionCompleteSentinel):
                # All records for a partition were generated
                if record_or_partition.partition not in partitions_to_done:
                    raise RuntimeError(
                        f"Received sentinel for partition {record_or_partition.partition} that was not in partitions. This is indicative of a bug in the CDK. Please contact support.partitions:\n{partitions_to_done}"
                    )
                partitions_to_done[record_or_partition.partition] = True
            elif isinstance(record_or_partition, Record):
                # Emit records
                yield record_or_partition.stream_data
            elif isinstance(record_or_partition, Partition):
                # A new partition was generated and must be processed
                partitions_to_done[record_or_partition] = False
                if self._slice_logger.should_log_slice_message(self.logger):
                    yield self._slice_logger.create_slice_log_message(record_or_partition.to_slice())
                futures.append(self._threadpool.submit(partition_reader.process_partition, record_or_partition))
            if finished_partitions and all(partitions_to_done.values()):
                # All partitions were generated and process. We're done here
                break
        self._check_for_errors(futures)

    def _check_for_errors(self, futures: List[Future[Any]]) -> None:
        exceptions_from_futures = [f for f in [future.exception() for future in futures] if f is not None]
        if exceptions_from_futures:
            raise RuntimeError(f"Failed reading from stream {self.name} with errors: {exceptions_from_futures}")
        futures_not_done = [f for f in futures if not f.done()]
        if futures_not_done:
            raise RuntimeError(f"Failed reading from stream {self.name} with futures not done: {futures_not_done}")

    @property
    def name(self) -> str:
        return self._name

    def check_availability(self) -> Tuple[bool, Optional[str]]:
        return self._availability_strategy.check_availability(self.logger)

    @property
    def primary_key(self) -> Optional[FieldPath]:
        return self._primary_key

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return self._cursor_field

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        return self._json_schema

    @property
    def source_defined_cursor(self) -> bool:
        return True

    @property
    def supports_incremental(self) -> bool:
        """
        :return: True if this stream supports incrementally reading data
        """
        # Incremental reads are not supported yet. This override should be deleted when incremental reads are supported.
        return False

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        return self._error_message_parser.get_error_display_message(exception)
