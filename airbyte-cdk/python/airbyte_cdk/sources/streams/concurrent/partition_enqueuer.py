#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from multiprocessing import Queue

from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.stream_thread_exception import StreamThreadException
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partitions.types import QueueItem


class PartitionEnqueuer:
    """
    Generates partitions from a partition generator and puts them in a queue.
    """

    def __init__(self, queue: Queue, sleep_time_in_seconds: float = 0.1) -> None:
        """
        :param queue:  The queue to put the partitions in.
        :param throttler: The throttler to use to throttle the partition generation.
        """
        self._queue = queue
        self._sleep_time_in_seconds = sleep_time_in_seconds

    def generate_partitions(self, stream: AbstractStream) -> None:
        """
        Generate partitions from a partition generator and put them in a queue.
        When all the partitions are added to the queue, a sentinel is added to the queue to indicate that all the partitions have been generated.

        If an exception is encountered, the exception will be caught and put in the queue. This is very important because if we don't, the
        main thread will have no way to know that something when wrong and will wait until the timeout is reached

        This method is meant to be called in a separate thread.
        """
        try:
            for partition in stream.generate_partitions():
                self._queue.put(partition)
            self._queue.put(PartitionGenerationCompletedSentinel(stream))
        except Exception as e:
            self._queue.put(StreamThreadException(e, stream.name))
            self._queue.put(PartitionGenerationCompletedSentinel(stream))
