#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import unittest
from queue import Queue
from typing import List
from unittest.mock import Mock, patch

import pytest
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.types import QueueItem, QueueItemObject


class PartitionEnqueuerTest(unittest.TestCase):
    def setUp(self) -> None:
        self._queue: Queue[QueueItemObject] = Queue()
        self._thread_pool_manager = Mock(spec=ThreadPoolManager)
        self._thread_pool_manager.prune_to_validate_has_reached_futures_limit.return_value = False
        self._partition_generator = PartitionEnqueuer(self._queue, self._thread_pool_manager)

    @patch("airbyte_cdk.sources.streams.concurrent.partition_enqueuer.time.sleep")
    def test_given_no_partitions_when_generate_partitions_then_do_not_wait(self, mocked_sleep):
        self._thread_pool_manager.prune_to_validate_has_reached_futures_limit.return_value = True  # shouldn't be called but just in case
        stream = self._a_stream([])

        self._partition_generator.generate_partitions(stream)

        assert mocked_sleep.call_count == 0

    def test_given_partitions_when_generate_partitions_then_only_push_sentinel(self):
        self._thread_pool_manager.prune_to_validate_has_reached_futures_limit.return_value = True
        stream = self._a_stream([])

        self._partition_generator.generate_partitions(stream)

        assert self._consume_queue() == [PartitionGenerationCompletedSentinel(stream)]

    def test_given_partitions_when_generate_partitions_then_return_partitions_before_sentinel(self):
        self._thread_pool_manager.prune_to_validate_has_reached_futures_limit.return_value = False
        partitions = [Mock(spec=Partition), Mock(spec=Partition)]
        stream = self._a_stream(partitions)

        self._partition_generator.generate_partitions(stream)

        assert self._consume_queue() == partitions + [PartitionGenerationCompletedSentinel(stream)]

    @patch("airbyte_cdk.sources.streams.concurrent.partition_enqueuer.time.sleep")
    def test_given_partition_but_limit_reached_when_generate_partitions_then_wait_until_not_hitting_limit(self, mocked_sleep):
        self._thread_pool_manager.prune_to_validate_has_reached_futures_limit.side_effect = [True, True, False]
        stream = self._a_stream([Mock(spec=Partition)])

        self._partition_generator.generate_partitions(stream)

        assert mocked_sleep.call_count == 2

    def test_given_exception_when_generate_partitions_then_raise(self):
        self._thread_pool_manager.prune_to_validate_has_reached_futures_limit.side_effect = ValueError()
        stream = Mock(spec=AbstractStream)
        stream.generate_partitions.side_effect = ValueError()

        with pytest.raises(ValueError):
            self._partition_generator.generate_partitions(stream)

    @staticmethod
    def _a_stream(partitions: List[Partition]) -> AbstractStream:
        stream = Mock(spec=AbstractStream)
        stream.generate_partitions.return_value = iter(partitions)
        return stream

    def _consume_queue(self) -> List[QueueItem]:
        queue_content = []
        while queue_item_object := self._queue.get():
            queue_item = queue_item_object.value
            if isinstance(queue_item, PartitionGenerationCompletedSentinel):
                queue_content.append(queue_item)
                break
            queue_content.append(queue_item)
        return queue_content
