#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import SinglePartitionRouter
from airbyte_cdk.sources.declarative.types import StreamSlice


def test():
    iterator = SinglePartitionRouter(parameters={})

    stream_slices = iterator.stream_slices()
    next_slice = next(stream_slices)
    assert next_slice == StreamSlice(partition={}, cursor_slice={})
