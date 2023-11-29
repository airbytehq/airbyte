#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue

from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partitions.types import QueueItem


class PartitionEnqueuer:
    """
    Generates partitions from a partition generator and puts them in a queue.
    """

    def __init__(self, queue: Queue[QueueItem]) -> None:
        """
        :param queue:  The queue to put the partitions in.
        :param sentinel: The sentinel to put in the queue when all the partitions have been generated.
        """
        self._queue = queue

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
                self._queue.put(partition)
            self._queue.put(PartitionGenerationCompletedSentinel(stream))
        except Exception as e:
            self._queue.put(e)
