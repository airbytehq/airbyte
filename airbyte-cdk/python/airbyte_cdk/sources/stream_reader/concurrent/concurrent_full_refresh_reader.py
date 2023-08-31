#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent
import concurrent.futures
import logging
from typing import Callable, Iterable, List, Optional

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
        # FIXME: need to either create them when reading, or reset them at the end of the read...
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
        partition_generator = self._partitions_generator_provider()
        partition_reader = self._partition_reader_provider()
        # Submit partition generation tasks
        partition_generator.generate_partitions_async(stream, SyncMode.full_refresh, cursor_field, self._threadpool, self)
        # While partitions are still being generated
        while not (partition_generator.is_done() and partition_reader.is_done()):
            self._check_for_errors(partition_generator, partition_reader, stream)

            # While there is a partition to process
            while partition_reader.there_are_records_ready():
                record = partition_reader.get_next_record()
                # print(f"found record to process: {record}")
                yield record.stream_data
                if FullRefreshStreamReader.is_record(record.stream_data):
                    total_records_counter += 1
                    if internal_config and internal_config.is_limit_reached(total_records_counter):
                        return
            while partition_generator.there_are_partitions_ready():
                partition = partition_generator.get_next_partition()
                print(f"found partition to process: {partition}")
                partition_reader.process_partition_async(partition, self._threadpool)
                print(f"processing partition {partition} for {stream.name}")
                if self._slice_logger.should_log_slice_message(logger):
                    # FIXME: This is creating slice log messages for parity with the synchronous implementation
                    # but these cannot be used by the connector builder to build slices because they can be unordered
                    yield self._slice_logger.create_slice_log_message(partition.slice)
            print(f"futures: {partition_generator._futures}")
            self._check_for_errors(partition_generator, partition_reader, stream)

    def _check_for_errors(self, partition_generator: PartitionGenerator, partition_reader: PartitionReader, stream: Stream) -> None:
        errors = []
        errors.extend(partition_generator.get_exceptions())
        errors.extend(partition_reader.get_exceptions())
        if errors:
            raise RuntimeError(f"Failed reading from stream {stream.name} with errors: {errors}")
