#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from concurrent.futures import Future
from queue import Queue
from typing import List, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import StreamPartition
from airbyte_cdk.sources.streams import Stream


class PartitionGenerator:
    def __init__(self, queue: Optional[Queue[StreamPartition]] = None):
        self._queue = queue if queue else Queue()
        self._futures: List[Future[None]] = []

    def generate_partitions(self, stream: Stream, sync_mode: SyncMode, cursor_field: Optional[List[str]]) -> None:
        stream.logger.debug(f"Generating partitions for stream {stream.name}")
        for partition in stream.generate_partitions(sync_mode=sync_mode, cursor_field=cursor_field):
            stream_partition = StreamPartition(stream, partition, cursor_field)
            self._queue.put(stream_partition)
        stream.logger.debug(f"Done generating partitions for stream {stream.name}")

    def has_next(self) -> bool:
        return self._queue.qsize() > 0

    def __iter__(self) -> "PartitionGenerator":
        return self

    def __next__(self) -> StreamPartition:
        if self._queue.qsize() > 0:
            return self._queue.get()
        else:
            raise StopIteration
