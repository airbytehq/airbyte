#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent
import concurrent.futures
import logging
from concurrent.futures import Future
from typing import Any, Callable, Iterable, List, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.stream_reader.concurrent.partition_generator import PartitionGenerator
from airbyte_cdk.sources.stream_reader.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams import FullRefreshStreamReader, Stream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import SliceLogger


class ConcurrentFullRefreshStreamReader(FullRefreshStreamReader):
    def __init__(
        self,
        partition_generator_provider: Callable[[], PartitionGenerator],
        partition_reader_provider: Callable[[], PartitionReader],
        max_workers: int,
        slice_logger: SliceLogger,
    ):
        self._partitions_generator_provider = partition_generator_provider
        self._partition_reader_provider = partition_reader_provider
        self._max_workers = max_workers
        self._slice_logger = slice_logger
        self._threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool")

    def read_stream(
        self, stream: Stream, cursor_field: Optional[List[str]], logger: logging.Logger, internal_config: InternalConfig = InternalConfig()
    ) -> Iterable[StreamData]:
        logger.debug(f"Processing stream slices for {stream.name} (sync_mode: full_refresh)")
        total_records_counter = 0
        futures = []
        partition_generator = self._partitions_generator_provider()
        partition_reader = self._partition_reader_provider()
        # Submit partition generation tasks
        futures.append(
            self._threadpool.submit(
                PartitionGenerator.generate_partitions, partition_generator, stream, SyncMode.full_refresh, cursor_field
            )
        )
        # While partitions are still being generated
        while partition_generator.has_next() or partition_reader.has_next() or not self._is_done(futures):
            self._check_for_errors(stream, futures)

            # While there is a partition to process
            for record in partition_reader:
                yield record._stream_data
                if FullRefreshStreamReader.is_record(record._stream_data):
                    total_records_counter += 1
                    if internal_config and internal_config.is_limit_reached(total_records_counter):
                        return
            for partition in partition_generator:
                futures.append(self._threadpool.submit(PartitionReader.process_partition, partition_reader, partition))
                if self._slice_logger.should_log_slice_message(logger):
                    # FIXME: This is creating slice log messages for parity with the synchronous implementation
                    # but these cannot be used by the connector builder to build slices because they can be unordered
                    yield self._slice_logger.create_slice_log_message(partition._slice)
        self._check_for_errors(stream, futures)

    def _is_done(self, futures: List[Future[Any]]) -> bool:
        return all(future.done() for future in futures)

    def _check_for_errors(self, stream: Stream, futures: List[Future[Any]]) -> None:
        exceptions_from_futures = [f for f in [future.exception() for future in futures] if f is not None]
        if exceptions_from_futures:
            raise RuntimeError(f"Failed reading from stream {stream.name} with errors: {exceptions_from_futures}")
