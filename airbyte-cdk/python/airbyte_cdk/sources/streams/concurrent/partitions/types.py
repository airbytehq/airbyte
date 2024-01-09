#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Union

from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.streams.concurrent.adapters import StreamPartition
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
QueueItem = Union[Record, Partition, StreamPartition, PartitionCompleteSentinel, PartitionGenerationCompletedSentinel, Exception]

class QueueItemObject:
    def __init__(self, item: QueueItem):
        self.value = item
        self._order = {
            PartitionGenerationCompletedSentinel: 0,
            PartitionCompleteSentinel: 1,
            Record: 2,
            Partition: 3,
            StreamPartition: 4,
        }
    def __lt__(self, other: "QueueItemObject"):
        if isinstance(self.value, Exception):
            return True
        elif isinstance(other.value, Exception):
            return False
        self_type_order = self._order[type(self.value)]
        other_type_order = other._order[type(other.value)]
        return self_type_order < other_type_order
