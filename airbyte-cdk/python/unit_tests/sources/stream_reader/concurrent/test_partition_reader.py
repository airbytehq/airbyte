#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

from airbyte_cdk.sources.stream_reader.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.stream_reader.concurrent.record import Record


def test_partition_reader_initially_has_no_output():
    partition_reader = PartitionReader()
    assert partition_reader.is_done()


def test_partition_reader():
    partition_reader = PartitionReader()

    stream_partition = Mock()
    records = [
        Record({"id": 1, "name": "Jack"}),
        Record({"id": 2, "name": "John"}),
    ]
    stream_partition.read.return_value = iter(records)

    assert partition_reader.is_done()

    partition_reader.process_partition(stream_partition)

    assert not partition_reader.is_done()

    actual_records = []
    while partition_reader.has_record_ready():
        actual_records.append(partition_reader.get_next())

    assert partition_reader.is_done()

    assert records == actual_records
