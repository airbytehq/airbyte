#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent
import concurrent.futures
import logging
from queue import Queue
from typing import Iterable, List, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.stream_reader.concurrent.partition_generator import PartitionGenerator
from airbyte_cdk.sources.stream_reader.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.stream_reader.concurrent.queue_consumer import _SENTINEL, QueueConsumer
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import StreamPartition
from airbyte_cdk.sources.stream_reader.full_refresh_stream_reader import FullRefreshStreamReader
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import SliceLogger


class ConcurrentStreamReader(FullRefreshStreamReader):
    def __init__(
        self,
        partition_generator: PartitionGenerator,
        partition_reader: PartitionReader,
        max_workers: int,
        slice_logger: SliceLogger,
    ):
        self._partitions_generator = partition_generator
        self._partition_reader = partition_reader
        self._max_workers = max_workers
        self._slice_logger = slice_logger

    def read_stream(
        self, stream: Stream, cursor_field: Optional[List[str]], logger: logging.Logger, internal_config: InternalConfig = InternalConfig()
    ) -> Iterable[StreamData]:
        logger.debug(f"Processing stream slices for {stream.name} (sync_mode: full_refresh)")
        total_records_counter = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool") as executor:
            # Submit partition generation tasks
            self._partitions_generator.generate_partitions_async(stream, SyncMode.full_refresh, cursor_field, executor)
            # While partitions are still being generated
            while not self._partitions_generator.is_done() or not self._partition_reader.is_done():
                # While there is a partition to process
                while self._partition_reader.there_are_records_ready():
                    record = self._partition_reader.get_next_record()
                    yield record.stream_data
                    if FullRefreshStreamReader.is_record(record.stream_data):
                        total_records_counter += 1
                        if internal_config and internal_config.is_limit_reached(total_records_counter):
                            return
                while self._partitions_generator.there_are_partitions_ready():
                    partition = self._partitions_generator.get_next_partition()
                    print(f"processing partition {partition} for {stream.name}")
                    if self._slice_logger.should_log_slice_message(logger):
                        # FIXME: This is creating slice log messages for parity with the synchronous implementation
                        # but these cannot be used by the connector builder to build slices because they can be unordered
                        yield self._slice_logger.create_slice_log_message(partition.slice)
                    self._partition_reader.process_partition_async(partition, executor)
