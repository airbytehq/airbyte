#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Union

from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record

PARTITIONS_GENERATED_SENTINEL = object


class PartitionCompleteSentinel:
    def __init__(self, partition: Partition):
        self.partition = partition


QueueItem = Union[Record, Partition, PartitionCompleteSentinel, PARTITIONS_GENERATED_SENTINEL, Partition]
