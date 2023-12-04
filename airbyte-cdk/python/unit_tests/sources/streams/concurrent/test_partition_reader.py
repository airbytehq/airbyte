#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue
from unittest.mock import Mock

from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel


def test_partition_reader():
    queue = Queue()
    partition_reader = PartitionReader(queue)

    stream_partition = Mock()
    records = [
        Record({"id": 1, "name": "Jack"}, "stream"),
        Record({"id": 2, "name": "John"}, "stream"),
    ]
    stream_partition.read.return_value = iter(records)

    partition_reader.process_partition(stream_partition)

    actual_records = []
    while record := queue.get():
        if isinstance(record, PartitionCompleteSentinel):
            break
        actual_records.append(record)

    assert records == actual_records
