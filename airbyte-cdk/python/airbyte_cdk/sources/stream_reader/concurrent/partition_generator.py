#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from concurrent.futures import Future
from queue import Queue
from typing import List, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import Partition
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import PartitionGenerator


class ConcurrentPartitionGenerator:
    def __init__(self):
        self._queue = Queue()
        self._futures: List[Future[None]] = []
        self._done = True

    def generate_partitions(self, partition_generator: PartitionGenerator, sync_mode: SyncMode, cursor_field: Optional[List[str]]) -> None:
        self._done = False
        for partition in partition_generator.generate(sync_mode=sync_mode, cursor_field=cursor_field):
            self._queue.put(partition)
        self._done = True

    def is_done(self) -> bool:
        return self._queue.qsize() == 0 and self._done

    def has_partition_ready(self) -> bool:
        return self._queue.qsize() > 0

    def get_next(self) -> Optional[Partition]:
        if self._queue.qsize() > 0:
            return self._queue.get()
        else:
            return None
