#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def read_full_refresh(stream_instance: Stream):
    records = []
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        records.extend(list(stream_instance.read_records(stream_slice=slice, sync_mode=SyncMode.full_refresh)))
    return records
