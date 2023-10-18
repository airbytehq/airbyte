#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.concurrent.partitions.partition_generator import PartitionGenerator
from airbyte_cdk.sources.streams.concurrent.partitions.types import PARTITIONS_GENERATED_SENTINEL, QueueItem


class PartitionEnqueuer:
    """
    Generates partitions from a partition generator and puts them in a queue.
    """

    def __init__(self, queue: Queue[QueueItem], sentinel: PARTITIONS_GENERATED_SENTINEL) -> None:
        """
        :param queue:  The queue to put the partitions in.
        :param sentinel: The sentinel to put in the queue when all the partitions have been generated.
        """
        self._queue = queue
        self._sentinel = sentinel

    def generate_partitions(self, partition_generator: PartitionGenerator, sync_mode: SyncMode) -> None:
        """
        Generate partitions from a partition generator and put them in a queue.
        When all the partitions are added to the queue, a sentinel is added to the queue to indicate that all the partitions have been generated.

        This method is meant to be called in a separate thread.
        :param partition_generator: The partition Generator
        :param sync_mode: The sync mode used
        :return:
        """
        for partition in partition_generator.generate(sync_mode=sync_mode):
            self._queue.put(partition)
        self._queue.put(self._sentinel)
