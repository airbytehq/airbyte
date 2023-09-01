#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue
from typing import Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.partitions.partition import Partition
from airbyte_cdk.sources.streams.partitions.partition_generator import PartitionGenerator


class ConcurrentPartitionGenerator:
    def __init__(self) -> None:
        self._queue: Queue[Partition] = Queue()
        self._done = True

    def generate_partitions(self, partition_generator: PartitionGenerator, sync_mode: SyncMode) -> None:
        self._done = False
        for partition in partition_generator.generate(sync_mode=sync_mode):
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
