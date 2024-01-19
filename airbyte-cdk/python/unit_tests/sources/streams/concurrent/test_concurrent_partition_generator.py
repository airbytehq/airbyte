#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, call

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.streams.concurrent.adapters import StreamPartition
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partitions.throttled_queue import ThrottledQueue


@pytest.mark.parametrize(
    "slices", [pytest.param([], id="test_no_partitions"), pytest.param([{"partition": 1}, {"partition": 2}], id="test_two_partitions")]
)
def test_partition_generator(slices):
    queue = Mock(spec=ThrottledQueue)
    partition_generator = PartitionEnqueuer(queue)

    stream = Mock()
    message_repository = Mock()
    sync_mode = SyncMode.full_refresh
    cursor_field = None
    state = None
    cursor = Mock()
    partitions = [StreamPartition(stream, s, message_repository, sync_mode, cursor_field, state, cursor) for s in slices]
    stream.generate_partitions.return_value = iter(partitions)

    partition_generator.generate_partitions(stream)

    assert queue.put.has_calls([call(p) for p in partitions] + [call(PartitionGenerationCompletedSentinel(stream))])
