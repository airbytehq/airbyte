#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from queue import Queue
from unittest.mock import Mock, patch

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.streams.concurrent.adapters import StreamPartition
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer


@pytest.mark.parametrize(
    "slices", [pytest.param([], id="test_no_partitions"), pytest.param([{"partition": 1}, {"partition": 2}], id="test_two_partitions")]
)
def test_partition_generator(slices):
    queue = Queue()
    max_size = 10
    wait_time = 0.1
    partition_generator = PartitionEnqueuer(queue, max_size, wait_time)

    stream = Mock()
    message_repository = Mock()
    sync_mode = SyncMode.full_refresh
    cursor_field = None
    state = None
    cursor = Mock()
    partitions = [StreamPartition(stream, s, message_repository, sync_mode, cursor_field, state, cursor) for s in slices]
    stream.generate_partitions.return_value = iter(partitions)

    partition_generator.generate_partitions(stream)

    actual_partitions = []
    while partition := queue.get(False):
        if isinstance(partition, PartitionGenerationCompletedSentinel):
            break
        actual_partitions.append(partition)

    assert actual_partitions == partitions

def test_generate_partitions_waits_if_too_many_items_in_queue():
    queue: Queue = Mock(spec=Queue)
    max_size = 1
    wait_time = 0.1
    partition_generator = PartitionEnqueuer(queue, max_size, wait_time)

    stream = Mock()
    partitions = [Mock()]
    stream.generate_partitions.return_value = iter(partitions)

    queue.qsize.side_effect = [2, 2]

    with patch("time.sleep") as sleep_mock:
        partition_generator.generate_partitions(stream)
        sleep_mock.assert_called_with(wait_time)
