import inspect
import unittest
from unittest.mock import Mock
from typing import Union

import pytest
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel, QueueItem, QueueItemObject


class QueueItemObjectTest(unittest.TestCase):

    def test_queue_item(self) -> None:
        # This test is a reminder for the devs that if QueueItem changes, `QueueItemObject.__lt__` needs to be updated
        assert QueueItem == Union[Record, Partition, PartitionCompleteSentinel, PartitionGenerationCompletedSentinel]

    def test_wrong_item_type_then_raise_exception(self):
        with pytest.raises(ValueError):
            QueueItemObject(1)

    def test_order(self) -> None:
        inspect.signature(Record.__init__)
        order_1_generation_completion = QueueItemObject(Mock(spec=PartitionGenerationCompletedSentinel))
        order_2_partition_completion = QueueItemObject(Mock(spec=PartitionCompleteSentinel))
        order_3_record = QueueItemObject(Mock(spec=Record))
        order_4_partition = QueueItemObject(Mock(spec=Partition))

        priority_order = sorted([
            order_1_generation_completion,
            order_3_record,
            order_4_partition,
            order_2_partition_completion,
        ])

        assert priority_order == [
            order_1_generation_completion,
            order_2_partition_completion,
            order_3_record,
            order_4_partition,
        ]
