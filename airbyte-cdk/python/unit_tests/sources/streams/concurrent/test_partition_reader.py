#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import unittest
from queue import Queue
from typing import Callable, Iterable, List
from unittest.mock import Mock

import pytest
from airbyte_cdk.sources.concurrent_source.stream_thread_exception import StreamThreadException
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel, QueueItem

_RECORDS = [
    Record({"id": 1, "name": "Jack"}, "stream"),
    Record({"id": 2, "name": "John"}, "stream"),
]


class PartitionReaderTest(unittest.TestCase):
    def setUp(self) -> None:
        self._queue: Queue[QueueItem] = Queue()
        self._partition_reader = PartitionReader(self._queue)

    def test_given_no_records_when_process_partition_then_only_emit_sentinel(self):
        self._partition_reader.process_partition(self._a_partition([]))

        while queue_item := self._queue.get():
            if not isinstance(queue_item, PartitionCompleteSentinel):
                pytest.fail("Only one PartitionCompleteSentinel is expected")
            break

    def test_given_read_partition_successful_when_process_partition_then_queue_records_and_sentinel(self):
        partition = self._a_partition(_RECORDS)
        self._partition_reader.process_partition(partition)

        queue_content = self._consume_queue()

        assert queue_content == _RECORDS + [PartitionCompleteSentinel(partition)]

    def test_given_exception_when_process_partition_then_queue_records_and_exception_and_sentinel(self):
        partition = Mock()
        exception = ValueError()
        partition.read.side_effect = self._read_with_exception(_RECORDS, exception)
        self._partition_reader.process_partition(partition)

        queue_content = self._consume_queue()

        assert queue_content == _RECORDS + [StreamThreadException(exception, partition.stream_name()), PartitionCompleteSentinel(partition)]

    def _a_partition(self, records: List[Record]) -> Partition:
        partition = Mock(spec=Partition)
        partition.read.return_value = iter(records)
        return partition

    @staticmethod
    def _read_with_exception(records: List[Record], exception: Exception) -> Callable[[], Iterable[Record]]:
        def mocked_function() -> Iterable[Record]:
            yield from records
            raise exception

        return mocked_function

    def _consume_queue(self):
        queue_content = []
        while queue_item := self._queue.get():
            queue_content.append(queue_item)
            if isinstance(queue_item, PartitionCompleteSentinel):
                break
        return queue_content
