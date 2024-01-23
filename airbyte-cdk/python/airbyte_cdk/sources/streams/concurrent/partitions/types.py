#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Union

from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record


class PartitionCompleteSentinel:
    """
    A sentinel object indicating all records for a partition were produced.
    Includes a pointer to the partition that was processed.
    """

    def __init__(self, partition: Partition):
        """
        :param partition: The partition that was processed
        """
        self.partition = partition


"""
Typedef representing the items that can be added to the ThreadBasedConcurrentStream
"""
QueueItem = Union[Record, Partition, PartitionCompleteSentinel, PartitionGenerationCompletedSentinel]


class QueueItemObject:

    def __init__(self, item: QueueItem):
        self.value = item
        self._priority = self._get_priority(self.value)

    @staticmethod
    def _get_priority(value: QueueItem) -> int:
        # The order of the `isinstance` is a bit funky but it is order in terms of which QueueItem we expect to see the most
        if isinstance(value, Record):
            return 3
        if isinstance(value, Partition):
            return 4
        if isinstance(value, PartitionCompleteSentinel):
            return 2
        if isinstance(value, PartitionGenerationCompletedSentinel):
            return 1

        raise ValueError(f"Unexpected type {type(value)}")

    def __lt__(self, other: "QueueItemObject") -> bool:
        return self._priority < other._priority
