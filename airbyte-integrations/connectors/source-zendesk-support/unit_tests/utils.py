#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def read_full_refresh(stream_instance: Stream):
    records = []
    schema = stream_instance.get_json_schema()
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        for record in stream_instance.read_records(stream_slice=slice, sync_mode=SyncMode.full_refresh):
            stream_instance.transformer.transform(record, schema)
            records.append(record)
    return records
