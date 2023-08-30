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
from airbyte_cdk.sources.stream_reader.concurrent.record import Record
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
        queue_consumer: QueueConsumer,
        queue: Queue[Optional[StreamPartition]],
        max_workers: int,
        slice_logger: SliceLogger,
    ):
        self._partitions_generator = partition_generator
        self._queue_consumer = queue_consumer
        self._queue = queue
        self._max_workers = max_workers
        self._slice_logger = slice_logger
        self._partition_reader = PartitionReader("partition_reader", Queue())

    def read_stream(
        self, stream: Stream, cursor_field: Optional[List[str]], logger: logging.Logger, internal_config: InternalConfig = InternalConfig()
    ) -> Iterable[StreamData]:
        logger.debug(f"Processing stream slices for {stream.name} (sync_mode: full_refresh)")
        total_records_counter = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers, thread_name_prefix="workerpool") as executor:
            try:
                # Submit partition generation tasks
                partition_generation_future = executor.submit(
                    PartitionGenerator.generate_partitions_for_stream,
                    self._partitions_generator,
                    stream,
                    SyncMode.full_refresh,
                    cursor_field,
                )
                # While partitions are still being generated
                while not partition_generation_future.done() or not self._partition_reader.is_done() or self._queue.qsize() > 0:
                    # While there is a partition to process
                    while self._partition_reader.there_are_records_ready():
                        record = self._partition_reader.get_next_record()
                        yield record.stream_data
                        if FullRefreshStreamReader.is_record(record.stream_data):
                            total_records_counter += 1
                            if internal_config and internal_config.is_limit_reached(total_records_counter):
                                return
                    while self._queue.qsize() > 0:
                        partition = self._queue.get()
                        print(f"processing partition {partition} for {stream.name}")
                        if self._slice_logger.should_log_slice_message(logger):
                            # FIXME: This is creating slice log messages for parity with the synchronous implementation
                            # but these cannot be used by the connector builder to build slices because they can be unordered
                            yield self._slice_logger.create_slice_log_message(partition.slice)
                        self._partition_reader.process_partition_async(partition, executor)
            except Exception as e:
                self._terminate_consumers()
                executor.shutdown(wait=True, cancel_futures=True)
                raise e

    def _get_num_dedicated_consumer_worker(self) -> int:
        # FIXME figure this out and add a unit test
        return int(max(self._max_workers / 2, 1))

    def _terminate_consumers(self):
        # FIXME: add a unit test
        for _ in range(self._get_num_dedicated_consumer_worker()):
            self._queue.put(_SENTINEL)

    def _futures_are_running(self, queue_consumer_futures):
        return not all(future.done() for future in queue_consumer_futures)
