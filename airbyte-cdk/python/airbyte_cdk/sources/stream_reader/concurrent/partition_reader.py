#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue
from typing import Optional

from airbyte_cdk.sources.stream_reader.concurrent.record import Record
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import StreamPartition


class PartitionReader:
    def __init__(self, output_queue: Optional[Queue[Record]] = None):
        self._output_queue = output_queue if output_queue else Queue()

    def process_partition(self, partition: StreamPartition) -> None:
        partition.get_logger().debug(f"Processing partition={partition}")
        for record in partition.read():
            self._output_queue.put(record)

    def has_next(self) -> bool:
        return self._output_queue.qsize() > 0

    def __iter__(self) -> "PartitionReader":
        return self

    def __next__(self) -> Record:
        if self._output_queue.qsize() > 0:
            return self._output_queue.get()
        else:
            raise StopIteration
