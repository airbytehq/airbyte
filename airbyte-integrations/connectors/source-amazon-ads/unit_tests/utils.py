#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterator, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]) -> Iterator[dict]:
    if stream_state and "state" in dir(stream_instance):
        stream_instance.state = stream_state

    slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
    for _slice in slices:
        records = stream_instance.read_records(sync_mode=SyncMode.incremental, stream_slice=_slice, stream_state=stream_state)
        for record in records:
            stream_state.clear()
            stream_state.update(stream_instance.get_updated_state(stream_state, record))
            yield record

        if hasattr(stream_instance, "state"):
            stream_state.clear()
            stream_state.update(stream_instance.state)
