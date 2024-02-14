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
QueueItem = Union[Record, Partition, PartitionCompleteSentinel, PartitionGenerationCompletedSentinel, Exception]
