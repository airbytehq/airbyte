#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.single_slice import SingleSlice


def test():
    iterator = SingleSlice(options={})

    stream_slices = iterator.stream_slices(SyncMode.incremental, None)
    assert stream_slices == [dict()]
