#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent
from concurrent.futures import Future
from functools import lru_cache
from queue import Queue
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import AbstractAvailabilityStrategy
from airbyte_cdk.sources.streams.concurrent.concurrent_partition_generator import ConcurrentPartitionGenerator
from airbyte_cdk.sources.streams.concurrent.error_message_parser import ErrorMessageParser
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader, PartitionSentinel
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.core import StreamData


class ThreadBasedConcurrentStream(AbstractStream):
    def __init__(
        self,
        partition_generator: PartitionGenerator,
        max_workers: int,
        name: str,
        json_schema: Mapping[str, Any],
        availability_strategy: Optional[AbstractAvailabilityStrategy],
        primary_key: Optional[Union[str, List[str], List[List[str]]]],
        cursor_field: Union[str, List[str]],
        error_display_message_parser: ErrorMessageParser,
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

    def read(self) -> Iterable[StreamData]:
        self.logger.debug(f"Processing stream slices for {self.name} (sync_mode: full_refresh)")
        futures = []
        queue = Queue()
        partition_sentinel = object()
        partition_generator = ConcurrentPartitionGenerator(queue, partition_sentinel)
        partition_reader = PartitionReader(queue)

        # Submit partition generation tasks
        futures.append(
            self._threadpool.submit(partition_generator.generate_partitions, self._stream_partition_generator, SyncMode.full_refresh)
        )

        TIMEOUT_SECONDS = 300

        partitions = {}

        finished_partitions = False
        while record_or_partition := queue.get(block=True, timeout=TIMEOUT_SECONDS):
            if record_or_partition == partition_sentinel:
                finished_partitions = True
            elif isinstance(record_or_partition, PartitionSentinel):
                partitions[record_or_partition.partition] = True
            elif self._is_record(record_or_partition):
                yield record_or_partition.stream_data
            elif self._is_partition(record_or_partition):
                partitions[record_or_partition] = False
                futures.append(self._threadpool.submit(partition_reader.process_partition, record_or_partition))
            # queue.qsize() is not reliable since it is possible for the queue to get modified, but we only check it if all futures are done
            if finished_partitions and all(p for p in partitions.values()):
                break
        self._check_for_errors(futures)

    def _is_record(self, record_or_partition):
        return isinstance(record_or_partition, Record)

    def _is_partition(self, record_or_partition):
        return isinstance(record_or_partition, Partition)

    def _check_for_errors(self, futures: List[Future[Any]]) -> None:
        exceptions_from_futures = [f for f in [future.exception() for future in futures] if f is not None]
        if exceptions_from_futures:
            raise RuntimeError(f"Failed reading from stream {self.name} with errors: {exceptions_from_futures}")

    @property
    def name(self) -> str:
        return self._name

    def check_availability(self) -> Tuple[bool, Optional[str]]:
        return self._availability_strategy.check_availability(self.logger)

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
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
