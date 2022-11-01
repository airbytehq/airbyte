#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]):
    res = []
    if stream_state and "state" in dir(stream_instance):
        stream_instance.state = stream_state
    slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
    for slice in slices:
        records = stream_instance.read_records(sync_mode=SyncMode.incremental, stream_slice=slice, stream_state=stream_state)
        for record in records:
            stream_state = stream_instance.get_updated_state(stream_state, record)
            res.append(record)
    return res, stream_state


def read_full_refresh(stream_instance: Stream):
    res = []
    schema = stream_instance.get_json_schema()
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        records = stream_instance.read_records(stream_slice=slice, sync_mode=SyncMode.full_refresh)
        for record in records:
            stream_instance.transformer.transform(record, schema)
            res.append(record)
    return res
