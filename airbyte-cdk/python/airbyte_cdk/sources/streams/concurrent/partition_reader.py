#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from multiprocessing import Queue

from airbyte_cdk.sources.concurrent_source.stream_thread_exception import StreamThreadException
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel, QueueItem


class PartitionReader:
    """
    Generates records from a partition and puts them in a queue.
    """
    @staticmethod
    def process_partition(partition: Partition, queue: Queue) -> None:
        """
        Process a partition and put the records in the output queue.
        When all the partitions are added to the queue, a sentinel is added to the queue to indicate that all the partitions have been generated.

        If an exception is encountered, the exception will be caught and put in the queue. This is very important because if we don't, the
        main thread will have no way to know that something when wrong and will wait until the timeout is reached

        This method is meant to be called from a thread.
        :param partition: The partition to read data from
        :return: None
        """
        try:
            for record in partition.read():
                queue.put(record)
            queue.put(PartitionCompleteSentinel(partition, is_successful=True))
        except Exception as e:
            queue.put(StreamThreadException(e, partition.stream_name()))
            queue.put(PartitionCompleteSentinel(partition, is_successful=False))
