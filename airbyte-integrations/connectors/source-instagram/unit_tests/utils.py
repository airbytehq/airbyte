#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]):
    res = []
    slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
    for slice in slices:
        records = stream_instance.read_records(sync_mode=SyncMode.incremental, stream_slice=slice, stream_state=stream_state)
        for record in records:
            stream_state = stream_instance.get_updated_state(stream_state, record)
            res.append(record)
    return res


def read_full_refresh(stream_instance: Stream):
    records = []
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        records.extend(list(stream_instance.read_records(stream_slice=slice, sync_mode=SyncMode.full_refresh)))
    return records
