#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from source_braze import DatetimeStreamSlicerComponent


def test_datetime_slicer():
    """
    - `step` to be added to stream slices.
    - `step` value one more higher than actual difference in days between end/start dates
    - `step` value exactly equal to difference in days between end/start dates for first slice item
    - take into account if difference in days between end/start dates less than `step` argument for last record
    """
    slicer = DatetimeStreamSlicerComponent(
        start_datetime="2022-12-01",
        end_datetime="2022-12-08",
        step="P3D",
        cursor_field="time",
        datetime_format="%Y-%m-%d",
        cursor_granularity="P1D",
        config={},
        options={},
        step_option=RequestOption(field_name="step", inject_into=RequestOptionType.request_parameter, options={})
    )
    expected_slices = [
        {'start_time': '2022-12-01', 'end_time': '2022-12-03', 'step': 2},
        {'start_time': '2022-12-04', 'end_time': '2022-12-06', 'step': 3},
        {'start_time': '2022-12-07', 'end_time': '2022-12-08', 'step': 2}
    ]
    assert slicer.stream_slices(SyncMode.incremental, stream_state={}) == expected_slices
