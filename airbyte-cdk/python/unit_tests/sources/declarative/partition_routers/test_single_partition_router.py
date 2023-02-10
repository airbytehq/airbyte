#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers.single_partition_router import SinglePartitionRouter


def test():
    iterator = SinglePartitionRouter(parameters={})

    stream_slices = iterator.stream_slices(SyncMode.incremental, None)
    next_slice = next(stream_slices)
    assert next_slice == dict()
