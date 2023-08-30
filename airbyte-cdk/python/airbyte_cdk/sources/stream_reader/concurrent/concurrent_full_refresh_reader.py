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

    def read_stream(
        self, stream: Stream, cursor_field: Optional[List[str]], logger: logging.Logger, internal_config: InternalConfig = InternalConfig()
    ) -> Iterable[StreamData]:
        logger.debug(f"Processing stream slices for {stream.name} (sync_mode: full_refresh)")
        partition_generation_futures = []
        queue_consumer_futures = []
        total_records_counter = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers + 10, thread_name_prefix="workerpool") as executor:
            try:
                # Submit partition generation tasks
                partition_generation_future = executor.submit(
                    PartitionGenerator.generate_partitions_for_stream,
                    self._partitions_generator,
                    stream,
                    SyncMode.full_refresh,
                    cursor_field,
                )
                partition_generation_futures.append(partition_generation_future)

                # Submit record generator tasks
                for i in range(self._get_num_dedicated_consumer_worker()):  # FIXME?
                    record_generation_future = executor.submit(QueueConsumer.consume_from_queue, self._queue_consumer, self._queue)
                    queue_consumer_futures.append(record_generation_future)

                # Wait for all partitions to be generated
                for future_partitions in concurrent.futures.as_completed(partition_generation_futures):
                    for stream_partition in future_partitions.result():
                        print(f"processing partition {stream_partition} for {stream.name}")
                        if self._slice_logger.should_log_slice_message(logger):
                            # FIXME: This is creating slice log messages for parity with the synchronous implementation
                            # but these cannot be used by the connector builder to build slices because they can be unordered
                            yield self._slice_logger.create_slice_log_message(stream_partition.slice)
                # Then put the sentinel on the queue
                self._terminate_consumers()
                # Wait for the consumers to finish
                # FIXME: We should start yielding as soon as the first ones are done...
                for future_records in concurrent.futures.as_completed(queue_consumer_futures):
                    # Each result is an iterable of record
                    result: List[Record] = future_records.result()
                    for record in result:
                        yield record.stream_data
                        if FullRefreshStreamReader.is_record(record.stream_data):
                            total_records_counter += 1
                            if internal_config and internal_config.is_limit_reached(total_records_counter):
                                return
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
