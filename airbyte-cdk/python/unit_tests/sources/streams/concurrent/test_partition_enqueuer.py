#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from queue import Queue
from unittest.mock import Mock

from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream, StreamAndStreamAvailability
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition


def test_enqueue_only_stream_availability_if_stream_is_not_available():
    queue = Queue()
    stream = Mock(spec=AbstractStream)

    stream.check_availability.return_value.is_available.return_value = False

    partition_enqueuer = PartitionEnqueuer(queue)

    partition_enqueuer.generate_partitions(stream)

    item = queue.get(False)
    assert isinstance(item, StreamAndStreamAvailability)
    assert item.stream == stream
    assert not item.availability.is_available()


def test_enqueue_partitions_and_sentinel_if_stream_is_available():
    queue = Queue()
    stream = Mock(spec=AbstractStream)

    stream.check_availability.return_value.is_available.return_value = True
    partition = Mock(spec=Partition)
    stream.generate_partitions.return_value = iter([partition])

    partition_enqueuer = PartitionEnqueuer(queue)

    partition_enqueuer.generate_partitions(stream)
    item = queue.get(False)
    assert isinstance(item, StreamAndStreamAvailability)
    assert item.stream == stream
    assert item.availability.is_available()

    item = queue.get(False)
    assert item == partition

    item = queue.get(False)
    assert isinstance(item, PartitionGenerationCompletedSentinel)
    assert item.stream == stream
