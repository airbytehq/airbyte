#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

from airbyte_cdk.sources.stream_reader.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.stream_reader.concurrent.record import Record


def test_partition_reader_initially_has_no_output():
    partition_reader = PartitionReader()
    assert not partition_reader.has_next()


def test_partition_reader():
    partition_reader = PartitionReader()

    stream_partition = Mock()
    records = [
        {"id": 1, "name": "Jack"},
        {"id": 2, "name": "John"},
    ]
    stream_partition.read.return_value = iter(records)

    partition_reader.process_partition(stream_partition)
    assert partition_reader.has_next()

    actual_records = list(r for r in partition_reader)
    assert not partition_reader.has_next()

    expected_records = [Record(d, stream_partition) for d in records]
    assert expected_records == actual_records
