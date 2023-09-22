#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator


class ConcurrentPartitionGenerator:
    def __init__(self, queue: Queue, sentinel) -> None:
        self._queue = queue
        self._sentinel = sentinel

    def generate_partitions(self, partition_generator: PartitionGenerator, sync_mode: SyncMode) -> None:
        """
        Generate partitions from a partition generator and put them in a queue.
        This method is meant to be called in a separate thread.
        :param partition_generator:
        :param sync_mode:
        :return:
        """
        for partition in partition_generator.generate(sync_mode=sync_mode):
            self._queue.put(partition)
        self._queue.put(self._sentinel)
