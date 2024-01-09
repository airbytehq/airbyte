#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue
import time

from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partitions.types import QueueItem, QueueItemObject


class PartitionEnqueuer:
    """
    Generates partitions from a partition generator and puts them in a queue.
    """

    def __init__(self, queue: Queue[QueueItem], max_size: int, wait_time: float) -> None:
        """
        :param queue:  The queue to put the partitions in.
        :param sentinel: The sentinel to put in the queue when all the partitions have been generated.
        :param max_size: The maximum size of the queue.
        :param wait_time: The time to wait between checking the queue size.
        """
        self._queue = queue
        self._max_size = max_size
        self._wait_time = wait_time

    def generate_partitions(self, stream: AbstractStream) -> None:
        """
        Generate partitions from a partition generator and put them in a queue.
        When all the partitions are added to the queue, a sentinel is added to the queue to indicate that all the partitions have been generated.

        If an exception is encountered, the exception will be caught and put in the queue.

        This method is meant to be called in a separate thread.
        :param partition_generator: The partition Generator
        :return:
        """
        try:
            for partition in stream.generate_partitions():
                while self._queue.qsize() >= self._max_size:
                    time.sleep(self._wait_time)
                self._queue.put(QueueItemObject(partition))
            self._queue.put(QueueItemObject(PartitionGenerationCompletedSentinel(stream)))
        except Exception as e:
            self._queue.put(QueueItemObject(e))
