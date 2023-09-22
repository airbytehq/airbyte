#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue

from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition


class PartitionSentinel:
    def __init__(self, partition):
        self.partition = partition


class PartitionReader:
    def __init__(self, queue: Queue) -> None:
        self._output_queue = queue

    def process_partition(self, partition: Partition) -> None:
        """
        Process a partition and put the records in the output queue.
        This method is meant to be called from a thread.
        :param partition:
        :return:
        """
        for record in partition.read():
            self._output_queue.put(record)
        self._output_queue.put(PartitionSentinel(partition))
