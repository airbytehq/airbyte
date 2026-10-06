#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from source_posthog.components import EventsCartesianProductStreamSlicer

from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.incremental.datetime_based_cursor import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.partition_routers.list_partition_router import ListPartitionRouter
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption


stream_slicers = [
    ListPartitionRouter(values=[2331], cursor_field="project_id", config={}, parameters={}),
    DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
        end_datetime=MinMaxDatetime(datetime="2021-02-01T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
        step="P10D",
        cursor_field="timestamp",
        datetime_format="%Y-%m-%dT%H:%M:%S.%f%z",
        cursor_granularity="PT0.000001S",
        start_time_option=RequestOption(inject_into="request_parameter", field_name="after", parameters={}),
        end_time_option=RequestOption(inject_into="request_parameter", field_name="before", parameters={}),
        config={},
        parameters={},
    ),
]


@pytest.mark.parametrize(
    "test_name, initial_state, stream_slice, last_record, expected_state",
    [
        ("test_empty", {}, {}, {}, {}),
        (
            "test_set_initial_state",
            {"2331": {"timestamp": "2021-01-01T00:00:00.00+0000"}},
            {},
            {},
            {"2331": {"timestamp": "2021-01-01T00:00:00.00+0000"}},
        ),
        (
            "test_update_empty_state",
            {},
            {"project_id": "2331", "start_time": "2021-01-01T00:00:00.00+0000", "end_time": "2021-01-03T00:00:00.00+0000"},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T11:00:00.00+0000"}},
        ),
        (
            "test_update_of_initial_state",
            {"2331": {"timestamp": "2021-01-01T10:00:00.00+0000"}},
            {"project_id": "2331", "start_time": "2021-01-01T00:00:00.00+0000", "end_time": "2021-01-03T00:00:00.00+0000"},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T11:00:00.00+0000"}},
        ),
        (
            "test_update_of_initial_state_newly",
            {"2331": {"timestamp": "2021-01-01T22:00:00.00+0000"}},
            {"project_id": "2331", "start_time": "2021-01-01T00:00:00.00+0000", "end_time": "2021-01-03T00:00:00.00+0000"},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T22:00:00.00+0000"}},
        ),
        (
            "test_update_of_initial_state_old_style",
            {"timestamp": "2021-01-01T10:00:00.00+0000"},
            {"project_id": "2331", "start_time": "2021-01-01T00:00:00.00+0000", "end_time": "2021-01-03T00:00:00.00+0000"},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T11:00:00.00+0000"}, "timestamp": "2021-01-01T10:00:00.00+0000"},
        ),
    ],
)
def test_update_cursor(test_name, initial_state, stream_slice, last_record, expected_state):
    slicer = EventsCartesianProductStreamSlicer(stream_slicers=stream_slicers, parameters={})
    # set initial state
    slicer.set_initial_state(initial_state)

    if last_record:
        slicer.close_slice(stream_slice, last_record)

    updated_state = slicer.get_stream_state()
    assert updated_state == expected_state


@pytest.mark.parametrize(
    "test_name, stream_state, expected_stream_slices",
    [
        (
            "test_empty_state",
            {},
            [
                {"end_time": "2021-01-10T23:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-01T00:00:00.000000+0000"},
                {"end_time": "2021-01-20T23:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-10T23:59:59.999999+0000"},
                {"end_time": "2021-01-30T23:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-20T23:59:59.999999+0000"},
                {"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-30T23:59:59.999999+0000"},
            ],
        ),
        (
            "test_state",
            {"2331": {"timestamp": "2021-01-01T17:00:00.000000+0000"}},
            [
                {"end_time": "2021-01-11T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-01T17:00:00.000000+0000"},
                {"end_time": "2021-01-21T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-11T16:59:59.999999+0000"},
                {"end_time": "2021-01-31T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-21T16:59:59.999999+0000"},
                {"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-31T16:59:59.999999+0000"},
            ],
        ),
        (
            "test_old_stype_state",
            {"timestamp": "2021-01-01T17:00:00.000000+0000"},
            [
                {"end_time": "2021-01-11T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-01T17:00:00.000000+0000"},
                {"end_time": "2021-01-21T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-11T16:59:59.999999+0000"},
                {"end_time": "2021-01-31T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-21T16:59:59.999999+0000"},
                {"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-31T16:59:59.999999+0000"},
            ],
        ),
        (
            "test_state_for_one_slice",
            {"2331": {"timestamp": "2021-01-27T17:00:00.000000+0000"}},
            [{"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-27T17:00:00.000000+0000"}],
        ),
    ],
)
def test_stream_slices(test_name, stream_state, expected_stream_slices):
    slicer = EventsCartesianProductStreamSlicer(stream_slicers=stream_slicers, parameters={})
    slicer.set_initial_state(stream_state)
    stream_slices = slicer.stream_slices()
    assert list(stream_slices) == expected_stream_slices
