#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue
from typing import Optional

from airbyte_cdk.sources.stream_reader.concurrent.record import Record
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import StreamPartition


class PartitionReader:
    def __init__(self):
        self._output_queue = Queue()
        self._done = True

    def process_partition(self, partition: StreamPartition) -> None:
        self._done = False
        partition.get_logger().debug(f"Processing partition={partition}")
        for record in partition.read():
            self._output_queue.put(record)
        self._done = True

    def is_done(self) -> bool:
        return self._output_queue.qsize() == 0 and self._done

    def has_record_ready(self) -> bool:
        return self._output_queue.qsize() > 0

    def get_next(self) -> Optional[Record]:
        if self._output_queue.qsize() > 0:
            return self._output_queue.get()
        else:
            return None
