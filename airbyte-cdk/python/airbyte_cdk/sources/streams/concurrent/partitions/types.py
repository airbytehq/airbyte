#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import List, Union

from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record

PARTITIONS_GENERATED_SENTINEL = object

FieldPath = Union[str, List[str]]


class PartitionCompleteSentinel:
    def __init__(self, partition: Partition):
        self.partition = partition


QueueItem = Union[Record, Partition, PartitionCompleteSentinel, PARTITIONS_GENERATED_SENTINEL, Partition]
