#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import SyncMode
from source_greenhouse.components import GreenHouseSlicer, GreenHouseSubstreamSlicer


def test_slicer():
    date_time = "2022-09-05T10:10:10.000000Z"
    date_time_dict = {date_time: date_time}
    slicer = GreenHouseSlicer(cursor_field=date_time, options=None, request_cursor_field=None)
    slicer.update_cursor(stream_slice=date_time_dict, last_record=date_time_dict)
    assert slicer.get_stream_state() == {date_time: "2022-09-05T10:10:10.000Z"}
    assert slicer.get_request_headers() == {}
    assert slicer.get_request_body_data() == {}
    assert slicer.get_request_body_json() == {}


@pytest.mark.parametrize(
    "last_record, expected, records",
    [
        (
            {"2022-09-05T10:10:10.000000Z": "2022-09-05T10:10:10.000000Z"},
            {"parent_key": {"2022-09-05T10:10:10.000000Z": "2022-09-05T10:10:10.000Z"}},
            [{"parent_key": "parent_key"}],
        ),
        (None, {}, []),
    ],
)
def test_sub_slicer(last_record, expected, records):
    date_time = "2022-09-05T10:10:10.000000Z"
    parent_slicer = GreenHouseSlicer(cursor_field=date_time, options=None, request_cursor_field=None)
    GreenHouseSlicer.read_records = MagicMock(return_value=records)
    slicer = GreenHouseSubstreamSlicer(
        cursor_field=date_time,
        options=None,
        request_cursor_field=None,
        parent_stream=parent_slicer,
        stream_slice_field=date_time,
        parent_key="parent_key",
    )
    stream_slice = next(slicer.stream_slices(SyncMode, {})) if records else {}
    slicer.update_cursor(stream_slice=stream_slice, last_record=last_record)
    assert slicer.get_stream_state() == expected
