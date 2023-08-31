#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue
from typing import Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.stream_reader.concurrent.record import Record
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import StreamPartition

_SENTINEL = None


class PartitionReader:
    def __init__(self, output_queue: Optional[Queue[Optional[Record]]] = None):
        self._output_queue = output_queue if output_queue else Queue()
        self._queue_consumer_futures = []

    def process_partition(self, partition: StreamPartition) -> None:
        partition.stream.logger.debug(f"Processing partition={partition}")
        for record in partition.stream.read_records(
            stream_slice=partition.slice, sync_mode=SyncMode.full_refresh, cursor_field=partition.cursor_field
        ):
            record = Record(record, partition)
            self._output_queue.put(record)

    def get_next_record(self) -> Optional[Record]:
        if self._output_queue.qsize() > 0:
            return self._output_queue.get()
        else:
            return None

    def has_next(self) -> bool:
        return self._output_queue.qsize() > 0

    def is_done(self) -> bool:
        return self._futures_are_done(self._queue_consumer_futures) and self._output_queue.qsize() == 0

    def process_partition_async(self, partition, executor):
        record_generation_future = executor.submit(PartitionReader.process_partition, self, partition)
        self._queue_consumer_futures.append(record_generation_future)

    def _futures_are_done(self, queue_consumer_futures):
        return all(future.done() for future in queue_consumer_futures)

    def get_exceptions(self):
        return [future.exception() for future in self._queue_consumer_futures if future.exception() is not None]
