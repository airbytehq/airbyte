#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.concurrent.concurrent_partition_generator import ConcurrentPartitionGenerator
from airbyte_cdk.sources.streams.partitions.legacy import LegacyPartition


@pytest.mark.parametrize(
    "slices", [pytest.param([], id="test_no_partitions"), pytest.param([{"partition": 1}, {"partition": 2}], id="test_two_partitions")]
)
def test_partition_generator(slices):
    partition_generator = ConcurrentPartitionGenerator()

    stream = Mock()
    partitions = [LegacyPartition(stream, s) for s in slices]
    stream.generate.return_value = iter(partitions)

    sync_mode = SyncMode.full_refresh

    assert partition_generator.is_done()

    partition_generator.generate_partitions(stream, sync_mode)

    assert partition_generator.is_done() == (len(partitions) == 0)

    actual_partitions = []
    while partition_generator.has_partition_ready():
        actual_partitions.append(partition_generator.get_next())

    assert partition_generator.is_done()

    assert actual_partitions == partitions
