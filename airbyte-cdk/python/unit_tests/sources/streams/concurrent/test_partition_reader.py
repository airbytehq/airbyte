#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue
from unittest.mock import Mock, patch

from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel


def test_partition_reader():
    queue = Queue()
    max_size = 10
    wait_time = 0.1
    partition_reader = PartitionReader(queue, max_size, wait_time)

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

def test_process_partition_waits_if_too_many_items_in_queue():
    queue: Queue = Mock(spec=Queue)
    max_size = 1
    wait_time = 0.1
    partition_reader = PartitionReader(queue, max_size, wait_time)

    stream = Mock()
    stream_partition = Mock()
    records = [
        Record({"id": 1, "name": "Jack"}, "stream"),
        Record({"id": 2, "name": "John"}, "stream"),
    ]
    stream_partition.read.return_value = iter(records)
    partitions = [Mock(), Mock()]
    stream.generate_partitions.return_value = iter(partitions)

    queue.qsize.side_effect = [2, 1]

    with patch("time.sleep") as sleep_mock:
        partition_reader.process_partition(stream_partition)
        sleep_mock.assert_called_with(wait_time)
