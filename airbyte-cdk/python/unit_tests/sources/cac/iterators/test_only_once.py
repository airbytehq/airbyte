#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.cac.iterators.only_once import OnlyOnceIterator


def test():
    iterator = OnlyOnceIterator()

    stream_slices = iterator.stream_slices(SyncMode.incremental, None)
    assert stream_slices == [dict()]
