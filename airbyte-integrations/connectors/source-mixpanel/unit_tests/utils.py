#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import urllib.parse

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def setup_response(status, body):
    return [{"json": body, "status_code": status}]


def get_url_to_mock(stream):
    return urllib.parse.urljoin(stream.url_base, stream.path())


def read_full_refresh(stream_instance: Stream):
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for _slice in slices:
        records = stream_instance.read_records(stream_slice=_slice, sync_mode=SyncMode.full_refresh)
        for record in records:
            yield record
