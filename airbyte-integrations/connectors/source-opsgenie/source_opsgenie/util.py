#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import SyncMode
from source_opsgenie.streams import OpsgenieStream


def read_full_refresh(stream_instance: OpsgenieStream):
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for _slice in slices:
        yield from stream_instance.read_records(stream_slice=_slice, sync_mode=SyncMode.full_refresh)
