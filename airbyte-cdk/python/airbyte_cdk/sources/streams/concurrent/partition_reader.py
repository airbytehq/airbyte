#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue
import time

from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel, QueueItem


class PartitionReader:
    """
    Generates records from a partition and puts them in a queue.
    """

    def __init__(self, queue: Queue[QueueItem]) -> None:
        """
        :param queue: The queue to put the records in.
        :param max_size: The maximum size of the queue. If the queue is full, the thread will wait for the specified amount of time before trying again.
        :param wait_time: The amount of time to wait before trying to put a record in the queue again.
        """
        self._queue = queue

    def process_partition(self, partition: Partition) -> None:
        """
        Process a partition and put the records in the output queue.
        When all the partitions are added to the queue, a sentinel is added to the queue to indicate that all the partitions have been generated.

        If an exception is encountered, the exception will be caught and put in the queue.

        This method is meant to be called from a thread.
        :param partition: The partition to read data from
        :return: None
        """
        try:
            for record in partition.read():
                self._queue.put(record)
            self._queue.put(PartitionCompleteSentinel(partition))
        except Exception as e:
            self._queue.put(e)
