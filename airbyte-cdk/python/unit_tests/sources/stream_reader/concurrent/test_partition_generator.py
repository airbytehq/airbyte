#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.stream_reader.concurrent.partition_generator import PartitionGenerator
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import StreamPartition


@pytest.mark.parametrize(
    "partitions", [pytest.param([], id="test_no_partitions"), pytest.param([{"partition": 1}, {"partition": 2}], id="test_two_partitions")]
)
def test_partition_generator(partitions):
    partition_generator = PartitionGenerator()

    stream = Mock()
    stream.generate_partitions.return_value = iter(partitions)

    sync_mode = SyncMode.full_refresh
    cursor_field = ["A_NESTED", "CURSOR_FIELD"]

    partition_generator.generate_partitions(stream, sync_mode, cursor_field)

    # assert the generator has partitions if the stream has partitions
    assert partition_generator.has_next() == (len(partitions) > 0)

    actual_partitions = [p for p in partition_generator]
    assert not partition_generator.has_next()

    expected_partitions = [StreamPartition(stream, p, cursor_field) for p in partitions]
    assert actual_partitions == expected_partitions
