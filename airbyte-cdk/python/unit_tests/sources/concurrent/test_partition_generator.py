#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from queue import Queue
from unittest.mock import Mock

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.concurrent.partition_generator import PartitionGenerator


@pytest.mark.parametrize(
    "partitions", [pytest.param([], id="test_no_partitions"), pytest.param([{"partition": 1}, {"partition": 2}], id="test_two_partitions")]
)
def test_partition_generator(partitions):
    queue = Queue()
    partition_generator = PartitionGenerator(queue, "A")

    stream = Mock()
    stream.generate_partitions.return_value = iter(partitions)

    sync_mode = SyncMode.full_refresh
    cursor_field = None  # FIXME need to pass it!

    assert queue.empty()

    actual_partitions = list(partition_generator.generate_partitions_for_stream(stream, sync_mode, cursor_field))

    assert actual_partitions == partitions

    partitions_from_queue = []
    while queue.qsize() > 0:
        partitions_from_queue.append(queue.get())

    expected_partitions_on_queue = [(p, stream) for p in partitions]
    assert partitions_from_queue == expected_partitions_on_queue
