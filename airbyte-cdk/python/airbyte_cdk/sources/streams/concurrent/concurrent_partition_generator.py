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
        """
        Generate partitions from a partition generator and put them in a queue.
        This method is meant to be called in a separate thread.
        :param partition_generator:
        :param sync_mode:
        :return:
        """
        self._done = False
        for partition in partition_generator.generate(sync_mode=sync_mode):
            self._queue.put(partition)
        self._done = True

    def is_done(self) -> bool:
        """
        Returns true if all the partitions were generated and read from the queue
        :return:
        """
        return self._queue.qsize() == 0 and self._done

    def has_partition_ready(self) -> bool:
        """
        Returns true if there is a partition ready to be read from the queue
        :return:
        """
        return self._queue.qsize() > 0

    def get_next(self) -> Optional[Partition]:
        """
        Returns the next partition in the queue or None if there is no partition ready
        :return:
        """
        if self._queue.qsize() > 0:
            return self._queue.get()
        else:
            return None
