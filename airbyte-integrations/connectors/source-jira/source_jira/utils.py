#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def safe_max(arg1, arg2):
    if arg1 is None:
        return arg2
    if arg2 is None:
        return arg1
    return max(arg1, arg2)


def read_full_refresh(stream_instance: Stream):
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for _slice in slices:
        records = stream_instance.read_records(stream_slice=_slice, sync_mode=SyncMode.full_refresh)
        for record in records:
            yield record


def read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]):
    slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
    for _slice in slices:
        records = stream_instance.read_records(sync_mode=SyncMode.incremental, stream_slice=_slice, stream_state=stream_state)
        for record in records:
            yield record
