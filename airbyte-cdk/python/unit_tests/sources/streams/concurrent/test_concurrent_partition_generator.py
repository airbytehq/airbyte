#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from queue import Queue
from unittest.mock import Mock

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.concurrent.legacy import LegacyPartition
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partitions.types import PARTITIONS_GENERATED_SENTINEL


@pytest.mark.parametrize(
    "slices", [pytest.param([], id="test_no_partitions"), pytest.param([{"partition": 1}, {"partition": 2}], id="test_two_partitions")]
)
def test_partition_generator(slices):
    queue = Queue()
    partition_generator = PartitionEnqueuer(queue, PARTITIONS_GENERATED_SENTINEL)

    stream = Mock()
    partitions = [LegacyPartition(stream, s) for s in slices]
    stream.generate.return_value = iter(partitions)

    sync_mode = SyncMode.full_refresh

    partition_generator.generate_partitions(stream, sync_mode)

    actual_partitions = []
    while partition := queue.get(False):
        if partition == PARTITIONS_GENERATED_SENTINEL:
            break
        actual_partitions.append(partition)

    assert actual_partitions == partitions
