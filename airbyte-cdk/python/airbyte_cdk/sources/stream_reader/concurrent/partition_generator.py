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
    def __init__(self):
        self._queue = Queue()
        self._futures: List[Future[None]] = []
        self._done = True

    def generate_partitions(self, stream: Stream, sync_mode: SyncMode, cursor_field: Optional[List[str]]) -> None:
        self._done = False
        stream.logger.debug(f"Generating partitions for stream {stream.name}")
        for partition in stream.generate_partitions(sync_mode=sync_mode, cursor_field=cursor_field):
            stream_partition = StreamPartition(stream, partition, cursor_field)
            self._queue.put(stream_partition)
        stream.logger.debug(f"Done generating partitions for stream {stream.name}")
        self._done = True

    def is_done(self) -> bool:
        return self._queue.qsize() == 0 and self._done

    def has_partition_ready(self) -> bool:
        return self._queue.qsize() > 0

    def get_next(self) -> Optional[StreamPartition]:
        if self._queue.qsize() > 0:
            return self._queue.get()
        else:
            return None
