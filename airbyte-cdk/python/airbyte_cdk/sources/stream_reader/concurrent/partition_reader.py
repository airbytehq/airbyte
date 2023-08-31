#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue
from typing import Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.stream_reader.concurrent.record import Record
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import StreamPartition


class PartitionReader:
    def __init__(self, output_queue: Optional[Queue[Optional[Record]]] = None):
        self._output_queue = output_queue if output_queue else Queue()

    def process_partition(self, partition: StreamPartition) -> None:
        partition.stream.logger.debug(f"Processing partition={partition}")
        for record in partition.stream.read_records(
            stream_slice=partition.slice, sync_mode=SyncMode.full_refresh, cursor_field=partition.cursor_field
        ):
            record = Record(record, partition)
            self._output_queue.put(record)

    def has_next(self) -> bool:
        return self._output_queue.qsize() > 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._output_queue.qsize() > 0:
            return self._output_queue.get()
        else:
            raise StopIteration
