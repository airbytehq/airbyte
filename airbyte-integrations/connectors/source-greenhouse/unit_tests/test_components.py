#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock, Mock

import pytest
from airbyte_cdk.sources.streams import Stream
# from source_greenhouse.components import GreenHouseSlicer, GreenHouseSubstreamSlicer


from unittest.mock import MagicMock, Mock

import pytest
from airbyte_cdk.sources.streams import Stream


@pytest.fixture
def greenhouse_slicer(components_module):
    GreenHouseSlicer = components_module.GreenHouseSlicer
    date_time = "2022-09-05T10:10:10.000000Z"
    return GreenHouseSlicer(cursor_field=date_time, parameters={}, request_cursor_field=None)


@pytest.fixture
def greenhouse_substream_slicer(components_module):
    GreenHouseSubstreamSlicer = components_module.GreenHouseSubstreamSlicer
    parent_stream = MagicMock(spec=Stream)
    return GreenHouseSubstreamSlicer(cursor_field='cursor_field', stream_slice_field='slice_field', parent_stream=parent_stream, parent_key='parent_key', parameters={}, request_cursor_field=None)

from unittest.mock import MagicMock, Mock

import pytest
from airbyte_cdk.sources.streams import Stream


@pytest.fixture
def greenhouse_slicer(components_module):
    GreenHouseSlicer = components_module.GreenHouseSlicer
    date_time = "2022-09-05T10:10:10.000000Z"
    return GreenHouseSlicer(cursor_field=date_time, parameters={}, request_cursor_field=None)


@pytest.fixture
def greenhouse_substream_slicer(components_module):
    GreenHouseSubstreamSlicer = components_module.GreenHouseSubstreamSlicer
    parent_stream = MagicMock(spec=Stream)
    return GreenHouseSubstreamSlicer(cursor_field='cursor_field', stream_slice_field='slice_field', parent_stream=parent_stream, parent_key='parent_key', parameters={}, request_cursor_field=None)

def test_slicer(greenhouse_slicer):
    date_time = "2022-09-05T10:10:10.000000Z"
    date_time_dict = {date_time: date_time}
    slicer = greenhouse_slicer
    slicer.close_slice(date_time_dict, date_time_dict)
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
def test_sub_slicer(components_module, last_record, expected, records):
    GreenHouseSubstreamSlicer = components_module.GreenHouseSubstreamSlicer
    date_time = "2022-09-05T10:10:10.000000Z"
    parent_stream = Mock(spec=Stream)
    parent_stream.stream_slices.return_value = [{"a slice": "value"}]
    parent_stream.read_records = MagicMock(return_value=records)
    slicer = GreenHouseSubstreamSlicer(
        cursor_field=date_time,
        parameters={},
        request_cursor_field=None,
        parent_stream=parent_stream,
        stream_slice_field=date_time,
        parent_key="parent_key",
    )
    stream_slice = next(slicer.stream_slices()) if records else {}
    slicer.close_slice(stream_slice, last_record)
    assert slicer.get_stream_state() == expected


@pytest.mark.parametrize(
    "stream_state, cursor_field, expected_state",
    [
        ({"cursor_field_1": "2022-09-05T10:10:10.000Z"}, "cursor_field_1", {"cursor_field_1": "2022-09-05T10:10:10.000Z"}),
        ({"cursor_field_2": "2022-09-05T10:10:100000Z"}, "cursor_field_3", {}),
        ({"cursor_field_4": None}, "cursor_field_4", {}),
        ({"cursor_field_5": ""}, "cursor_field_5", {}),
    ],
    ids=["cursor_value_present", "cursor_value_not_present", "cursor_value_is_None", "cursor_value_is_empty_string"],
)
def test_slicer_set_initial_state(components_module, stream_state, cursor_field, expected_state):
    GreenHouseSlicer = components_module.GreenHouseSlicer
    slicer = GreenHouseSlicer(cursor_field=cursor_field, parameters={}, request_cursor_field=None)
    # Set initial state
    slicer.set_initial_state(stream_state)
    assert slicer.get_stream_state() == expected_state


@pytest.mark.parametrize(
    "stream_state, initial_state, expected_state",
    [
        (
            {"id1": {"cursor_field": "2023-01-01T10:00:00.000Z"}},
            {"id2": {"cursor_field": "2023-01-02T11:00:00.000Z"}},
            {"id1": {"cursor_field": "2023-01-01T10:00:00.000Z"}, "id2": {"cursor_field": "2023-01-02T11:00:00.000Z"}},
        ),
        (
            {"id1": {"cursor_field": "2023-01-01T10:00:00.000Z"}},
            {"id1": {"cursor_field": "2023-01-01T09:00:00.000Z"}},
            {"id1": {"cursor_field": "2023-01-01T10:00:00.000Z"}},
        ),
        ({}, {}, {}),
    ],
    ids=[
        "stream_state and initial_state have different keys",
        "stream_state and initial_state have overlapping keys with different values",
        "stream_state and initial_state are empty",
    ],
)
def test_substream_set_initial_state(greenhouse_substream_slicer, stream_state, initial_state, expected_state):
    slicer = greenhouse_substream_slicer
    # Set initial state
    slicer._state = initial_state
    slicer.set_initial_state(stream_state)
    assert slicer._state == expected_state


@pytest.mark.parametrize(
    "first_record, second_record, expected_result",
    [
        ({"cursor_field": "2023-01-01T00:00:00.000Z"}, {"cursor_field": "2023-01-02T00:00:00.000Z"}, False),
        ({"cursor_field": "2023-02-01T00:00:00.000Z"}, {"cursor_field": "2023-01-01T00:00:00.000Z"}, True),
        ({"cursor_field": "2023-01-02T00:00:00.000Z"}, {"cursor_field": ""}, True),
        ({"cursor_field": ""}, {"cursor_field": "2023-01-02T00:00:00.000Z"}, False),
    ],
)
def test_is_greater_than_or_equal(greenhouse_substream_slicer, first_record, second_record, expected_result):
    slicer = greenhouse_substream_slicer
    assert slicer.is_greater_than_or_equal(first_record, second_record) == expected_result