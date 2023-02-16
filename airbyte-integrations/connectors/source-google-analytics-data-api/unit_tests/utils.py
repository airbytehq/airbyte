#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]):
    slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
    for _slice in slices:
        records = stream_instance.read_records(sync_mode=SyncMode.incremental, stream_slice=_slice, stream_state=stream_state)
        for record in records:
            stream_state = stream_instance.get_updated_state(stream_state, record)
            yield record
