#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dateutil.parser
import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def dateutil_parse(text):
    """
    The custom function `dateutil_parse` replace `pendulum.parse(text, strict=False)` to avoid memory leak.
    More details https://github.com/airbytehq/airbyte/pull/19913
    """
    dt = dateutil.parser.parse(text)
    return pendulum.datetime(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second,
        dt.microsecond,
        tz=dt.tzinfo or pendulum.tz.UTC,
    )


def read_full_refresh(stream_instance: Stream):
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for _slice in slices:
        for record in stream_instance.read_records(stream_slice=_slice, sync_mode=SyncMode.full_refresh):
            yield record
