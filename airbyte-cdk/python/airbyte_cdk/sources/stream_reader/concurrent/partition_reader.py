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
    def __init__(self, name: str, output_queue: Queue[Optional[Record]]):
        self._name = name
        self._output_queue = output_queue
        self._queue_consumer_futures = []

    def process_partition(self, partition: StreamPartition) -> None:
        print(f"{self._name} is processing partition={partition}")
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

    def there_are_records_ready(self) -> bool:
        return self._output_queue.qsize() > 0

    def is_done(self) -> bool:
        done = self._output_queue.qsize() == 0 and self._futures_are_done(self._queue_consumer_futures)
        print(f"{self._name} is done: {done}")
        return done

    def process_partition_async(self, partition, executor):
        record_generation_future = executor.submit(PartitionReader.process_partition, self, partition)
        self._queue_consumer_futures.append(record_generation_future)

    def _futures_are_done(self, queue_consumer_futures):
        return all(future.done() for future in queue_consumer_futures)
