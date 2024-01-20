#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import unittest

import pytest
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.types import Record

datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
cursor_granularity = "PT0.000001S"
FAKE_NOW = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)

config = {"start_date": "2021-01-01T00:00:00.000000+0000", "start_date_ymd": "2021-01-01"}
end_date_now = InterpolatedString(string="{{ today_utc() }}", parameters={})
cursor_field = "created"
timezone = datetime.timezone.utc
NO_STATE = {}
ANY_SLICE = {}


class MockedNowDatetime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return FAKE_NOW


@pytest.fixture()
def mock_datetime_now(monkeypatch):
    monkeypatch.setattr(datetime, "datetime", MockedNowDatetime)


@pytest.mark.parametrize(
    "test_name, stream_state, start, end, step, cursor_field, lookback_window, datetime_format, cursor_granularity, expected_slices",
    [
        (
            "test_1_day",
            NO_STATE,
            MinMaxDatetime(datetime="{{ config['start_date'] }}", parameters={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
            "P1D",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-01T23:59:59.999999+0000"},
                {"start_time": "2021-01-02T00:00:00.000000+0000", "end_time": "2021-01-02T23:59:59.999999+0000"},
                {"start_time": "2021-01-03T00:00:00.000000+0000", "end_time": "2021-01-03T23:59:59.999999+0000"},
                {"start_time": "2021-01-04T00:00:00.000000+0000", "end_time": "2021-01-04T23:59:59.999999+0000"},
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T23:59:59.999999+0000"},
                {"start_time": "2021-01-06T00:00:00.000000+0000", "end_time": "2021-01-06T23:59:59.999999+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-07T23:59:59.999999+0000"},
                {"start_time": "2021-01-08T00:00:00.000000+0000", "end_time": "2021-01-08T23:59:59.999999+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-09T23:59:59.999999+0000"},
                {"start_time": "2021-01-10T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_2_day",
            NO_STATE,
            MinMaxDatetime(datetime="{{ config['start_date'] }}", parameters={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
            "P2D",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-02T23:59:59.999999+0000"},
                {"start_time": "2021-01-03T00:00:00.000000+0000", "end_time": "2021-01-04T23:59:59.999999+0000"},
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-06T23:59:59.999999+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-08T23:59:59.999999+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_1_week",
            NO_STATE,
            MinMaxDatetime(datetime="{{ config['start_date'] }}", parameters={}),
            MinMaxDatetime(datetime="2021-02-10T00:00:00.000000+0000", parameters={}),
            "P1W",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-07T23:59:59.999999+0000"},
                {"start_time": "2021-01-08T00:00:00.000000+0000", "end_time": "2021-01-14T23:59:59.999999+0000"},
                {"start_time": "2021-01-15T00:00:00.000000+0000", "end_time": "2021-01-21T23:59:59.999999+0000"},
                {"start_time": "2021-01-22T00:00:00.000000+0000", "end_time": "2021-01-28T23:59:59.999999+0000"},
                {"start_time": "2021-01-29T00:00:00.000000+0000", "end_time": "2021-02-04T23:59:59.999999+0000"},
                {"start_time": "2021-02-05T00:00:00.000000+0000", "end_time": "2021-02-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_1_month",
            NO_STATE,
            MinMaxDatetime(datetime="{{ config['start_date'] }}", parameters={}),
            MinMaxDatetime(datetime="2021-06-10T00:00:00.000000+0000", parameters={}),
            "P1M",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-31T23:59:59.999999+0000"},
                {"start_time": "2021-02-01T00:00:00.000000+0000", "end_time": "2021-02-28T23:59:59.999999+0000"},
                {"start_time": "2021-03-01T00:00:00.000000+0000", "end_time": "2021-03-31T23:59:59.999999+0000"},
                {"start_time": "2021-04-01T00:00:00.000000+0000", "end_time": "2021-04-30T23:59:59.999999+0000"},
                {"start_time": "2021-05-01T00:00:00.000000+0000", "end_time": "2021-05-31T23:59:59.999999+0000"},
                {"start_time": "2021-06-01T00:00:00.000000+0000", "end_time": "2021-06-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_1_year",
            NO_STATE,
            MinMaxDatetime(datetime="{{ config['start_date'] }}", parameters={}),
            MinMaxDatetime(datetime="2022-06-10T00:00:00.000000+0000", parameters={}),
            "P1Y",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-12-31T23:59:59.999999+0000"},
                {"start_time": "2022-01-01T00:00:00.000000+0000", "end_time": "2022-01-01T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_from_stream_state",
            {cursor_field: "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="2020-01-05T00:00:00.000000+0000", parameters={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
            "P1D",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T23:59:59.999999+0000"},
                {"start_time": "2021-01-06T00:00:00.000000+0000", "end_time": "2021-01-06T23:59:59.999999+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-07T23:59:59.999999+0000"},
                {"start_time": "2021-01-08T00:00:00.000000+0000", "end_time": "2021-01-08T23:59:59.999999+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-09T23:59:59.999999+0000"},
                {"start_time": "2021-01-10T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_12_day",
            NO_STATE,
            MinMaxDatetime(datetime="{{ config['start_date'] }}", parameters={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
            "P12D",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_end_time_greater_than_now",
            NO_STATE,
            MinMaxDatetime(datetime="2021-12-28T00:00:00.000000+0000", parameters={}),
            MinMaxDatetime(datetime=f"{(FAKE_NOW + datetime.timedelta(days=1)).strftime(datetime_format)}", parameters={}),
            "P1D",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-12-28T00:00:00.000000+0000", "end_time": "2021-12-28T23:59:59.999999+0000"},
                {"start_time": "2021-12-29T00:00:00.000000+0000", "end_time": "2021-12-29T23:59:59.999999+0000"},
                {"start_time": "2021-12-30T00:00:00.000000+0000", "end_time": "2021-12-30T23:59:59.999999+0000"},
                {"start_time": "2021-12-31T00:00:00.000000+0000", "end_time": "2021-12-31T23:59:59.999999+0000"},
                {"start_time": "2022-01-01T00:00:00.000000+0000", "end_time": "2022-01-01T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_start_date_greater_than_end_time",
            NO_STATE,
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
            MinMaxDatetime(datetime="2021-01-05T00:00:00.000000+0000", parameters={}),
            "P1D",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_cursor_date_greater_than_start_date",
            {cursor_field: "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", parameters={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
            "P1D",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T23:59:59.999999+0000"},
                {"start_time": "2021-01-06T00:00:00.000000+0000", "end_time": "2021-01-06T23:59:59.999999+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-07T23:59:59.999999+0000"},
                {"start_time": "2021-01-08T00:00:00.000000+0000", "end_time": "2021-01-08T23:59:59.999999+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-09T23:59:59.999999+0000"},
                {"start_time": "2021-01-10T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_cursor_date_greater_than_start_date_multiday_step",
            {cursor_field: "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="2021-01-03T00:00:00.000000+0000", parameters={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
            "P2D",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-06T23:59:59.999999+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-08T23:59:59.999999+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_with_lookback_window_from_start_date",
            NO_STATE,
            MinMaxDatetime(datetime="2021-01-05", datetime_format="%Y-%m-%d", parameters={}),
            MinMaxDatetime(datetime="2021-01-05", datetime_format="%Y-%m-%d", parameters={}),
            "P1D",
            cursor_field,
            "P3D",
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-02T00:00:00.000000+0000", "end_time": "2021-01-02T23:59:59.999999+0000"},
                {"start_time": "2021-01-03T00:00:00.000000+0000", "end_time": "2021-01-03T23:59:59.999999+0000"},
                {"start_time": "2021-01-04T00:00:00.000000+0000", "end_time": "2021-01-04T23:59:59.999999+0000"},
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_with_lookback_window_from_cursor",
            {cursor_field: "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", parameters={}),
            MinMaxDatetime(datetime="2021-01-06T00:00:00.000000+0000", parameters={}),
            "P1D",
            cursor_field,
            "P3D",
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-02T00:00:00.000000+0000", "end_time": "2021-01-02T23:59:59.999999+0000"},
                {"start_time": "2021-01-03T00:00:00.000000+0000", "end_time": "2021-01-03T23:59:59.999999+0000"},
                {"start_time": "2021-01-04T00:00:00.000000+0000", "end_time": "2021-01-04T23:59:59.999999+0000"},
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T23:59:59.999999+0000"},
                {"start_time": "2021-01-06T00:00:00.000000+0000", "end_time": "2021-01-06T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_with_lookback_window_defaults_to_0d",
            {},
            MinMaxDatetime(datetime="2021-01-01", datetime_format="%Y-%m-%d", parameters={}),
            MinMaxDatetime(datetime="2021-01-05", datetime_format="%Y-%m-%d", parameters={}),
            "P1D",
            cursor_field,
            "{{ config['does_not_exist'] }}",
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-01T23:59:59.999999+0000"},
                {"start_time": "2021-01-02T00:00:00.000000+0000", "end_time": "2021-01-02T23:59:59.999999+0000"},
                {"start_time": "2021-01-03T00:00:00.000000+0000", "end_time": "2021-01-03T23:59:59.999999+0000"},
                {"start_time": "2021-01-04T00:00:00.000000+0000", "end_time": "2021-01-04T23:59:59.999999+0000"},
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_start_is_after_stream_state",
            {cursor_field: "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", parameters={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
            "P1D",
            cursor_field,
            None,
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T23:59:59.999999+0000"},
                {"start_time": "2021-01-06T00:00:00.000000+0000", "end_time": "2021-01-06T23:59:59.999999+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-07T23:59:59.999999+0000"},
                {"start_time": "2021-01-08T00:00:00.000000+0000", "end_time": "2021-01-08T23:59:59.999999+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-09T23:59:59.999999+0000"},
                {"start_time": "2021-01-10T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
    ],
)
def test_stream_slices(
    mock_datetime_now,
    test_name,
    stream_state,
    start,
    end,
    step,
    cursor_field,
    lookback_window,
    datetime_format,
    cursor_granularity,
    expected_slices,
):
    lookback_window = InterpolatedString(string=lookback_window, parameters={}) if lookback_window else None
    cursor = DatetimeBasedCursor(
        start_datetime=start,
        end_datetime=end,
        step=step,
        cursor_field=cursor_field,
        datetime_format=datetime_format,
        cursor_granularity=cursor_granularity,
        lookback_window=lookback_window,
        config=config,
        parameters={},
    )
    cursor.set_initial_state(stream_state)
    stream_slices = cursor.stream_slices()

    assert stream_slices == expected_slices


@pytest.mark.parametrize(
    "test_name, previous_cursor, stream_slice, latest_record_data, expected_state",
    [
        (
            "test_close_slice_previous_cursor_is_highest",
            "2023-01-01",
            {"end_time": "2022-01-01"},
            {cursor_field: "2021-01-01"},
            {cursor_field: "2023-01-01"},
        ),
        (
            "test_close_slice_stream_slice_partition_end_is_highest",
            "2021-01-01",
            {"end_time": "2023-01-01"},
            {cursor_field: "2021-01-01"},
            {cursor_field: "2023-01-01"},
        ),
        (
            "test_close_slice_latest_record_cursor_value_is_highest",
            "2021-01-01",
            {"end_time": "2022-01-01"},
            {cursor_field: "2023-01-01"},
            {cursor_field: "2023-01-01"},
        ),
        (
            "test_close_slice_without_latest_record",
            "2021-01-01",
            {"end_time": "2022-01-01"},
            None,
            {cursor_field: "2022-01-01"},
        ),
        (
            "test_close_slice_without_cursor",
            None,
            {"end_time": "2022-01-01"},
            {cursor_field: "2023-01-01"},
            {cursor_field: "2023-01-01"},
        ),
    ],
)
def test_close_slice(test_name, previous_cursor, stream_slice, latest_record_data, expected_state):
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", parameters={}),
        cursor_field=InterpolatedString(string=cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    cursor._cursor = previous_cursor
    cursor.close_slice(stream_slice, Record(latest_record_data, stream_slice) if latest_record_data else None)
    updated_state = cursor.get_stream_state()
    assert updated_state == expected_state


def test_given_different_format_and_slice_is_highest_when_close_slice_then_slice_datetime_format():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", parameters={}),
        cursor_field=cursor_field,
        datetime_format="%Y-%m-%dT%H:%M:%S.%fZ",
        cursor_datetime_formats=["%Y-%m-%d"],
        config=config,
        parameters={},
    )

    _slice = {"end_time": "2023-01-04T17:30:19.000Z"}
    record_cursor_value = "2023-01-03"
    cursor.close_slice(_slice, Record({cursor_field: record_cursor_value}, _slice))

    assert cursor.get_stream_state()[cursor_field] == "2023-01-04T17:30:19.000Z"


def test_given_partition_end_is_specified_and_greater_than_record_when_close_slice_then_use_partition_end():
    partition_field_end = "partition_field_end"
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", parameters={}),
        cursor_field=InterpolatedString(string=cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        partition_field_end=partition_field_end,
        config=config,
        parameters={},
    )
    stream_slice = {partition_field_end: "2025-01-01"}
    cursor.close_slice(stream_slice, Record({cursor_field: "2020-01-01"}, stream_slice))
    updated_state = cursor.get_stream_state()
    assert {cursor_field: "2025-01-01"} == updated_state


@pytest.mark.parametrize(
    "test_name, inject_into, field_name, expected_req_params, expected_headers, expected_body_json, expected_body_data",
    [
        ("test_start_time_inject_into_none", None, None, {}, {}, {}, {}),
        (
            "test_start_time_passed_by_req_param",
            RequestOptionType.request_parameter,
            "start_time",
            {"start_time": "2021-01-01T00:00:00.000000+0000", "endtime": "2021-01-04T00:00:00.000000+0000"},
            {},
            {},
            {},
        ),
        (
            "test_start_time_inject_into_header",
            RequestOptionType.header,
            "start_time",
            {},
            {"start_time": "2021-01-01T00:00:00.000000+0000", "endtime": "2021-01-04T00:00:00.000000+0000"},
            {},
            {},
        ),
        (
            "test_start_time_inject_intoy_body_json",
            RequestOptionType.body_json,
            "start_time",
            {},
            {},
            {"start_time": "2021-01-01T00:00:00.000000+0000", "endtime": "2021-01-04T00:00:00.000000+0000"},
            {},
        ),
        (
            "test_start_time_inject_into_body_data",
            RequestOptionType.body_data,
            "start_time",
            {},
            {},
            {},
            {"start_time": "2021-01-01T00:00:00.000000+0000", "endtime": "2021-01-04T00:00:00.000000+0000"},
        ),
    ],
)
def test_request_option(test_name, inject_into, field_name, expected_req_params, expected_headers, expected_body_json, expected_body_data):
    start_request_option = RequestOption(inject_into=inject_into, parameters={}, field_name=field_name) if inject_into else None
    end_request_option = RequestOption(inject_into=inject_into, parameters={}, field_name="endtime") if inject_into else None
    slicer = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", parameters={}),
        end_datetime=MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
        step="P1D",
        cursor_field=InterpolatedString(string=cursor_field, parameters={}),
        datetime_format=datetime_format,
        cursor_granularity=cursor_granularity,
        lookback_window=InterpolatedString(string="P0D", parameters={}),
        start_time_option=start_request_option,
        end_time_option=end_request_option,
        config=config,
        parameters={},
    )
    stream_slice = {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-04T00:00:00.000000+0000"}
    assert expected_req_params == slicer.get_request_params(stream_slice=stream_slice)
    assert expected_headers == slicer.get_request_headers(stream_slice=stream_slice)
    assert expected_body_json == slicer.get_request_body_json(stream_slice=stream_slice)
    assert expected_body_data == slicer.get_request_body_data(stream_slice=stream_slice)


@pytest.mark.parametrize(
    "test_name, input_date, date_format, date_format_granularity, expected_output_date",
    [
        (
            "test_parse_date_iso",
            "2021-01-01T00:00:00.000000+0000",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "PT0.000001S",
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        (
            "test_parse_timestamp",
            "1609459200",
            "%s",
            "PT1S",
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        ("test_parse_date_number", "20210101", "%Y%m%d", "P1D", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)),
    ],
)
def test_parse_date_legacy_merge_datetime_format_in_cursor_datetime_format(
    test_name, input_date, date_format, date_format_granularity, expected_output_date
):
    slicer = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2021-01-01T00:00:00.000000+0000", parameters={}),
        end_datetime=MinMaxDatetime("2021-01-10T00:00:00.000000+0000", parameters={}),
        step="P1D",
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format=date_format,
        cursor_granularity=date_format_granularity,
        lookback_window=InterpolatedString("P0D", parameters={}),
        config=config,
        parameters={},
    )
    output_date = slicer.parse_date(input_date)
    assert expected_output_date == output_date


@pytest.mark.parametrize(
    "test_name, input_date, date_formats, expected_output_date",
    [
        (
            "test_match_first_format",
            "2021-01-01T00:00:00.000000+0000",
            ["%Y-%m-%dT%H:%M:%S.%f%z", "%s"],
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        (
            "test_match_second_format",
            "1609459200",
            ["%Y-%m-%dT%H:%M:%S.%f%z", "%s"],
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        ),
    ],
)
def test_parse_date(test_name, input_date, date_formats, expected_output_date):
    slicer = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2021-01-01T00:00:00.000000+0000", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        cursor_datetime_formats=date_formats,
        config=config,
        parameters={},
    )
    assert slicer.parse_date(input_date) == expected_output_date


def test_given_unknown_format_when_parse_date_then_raise_error():
    slicer = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2021-01-01T00:00:00.000000+0000", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        cursor_datetime_formats=["%Y-%m-%d", "%s"],
        config=config,
        parameters={},
    )
    with pytest.raises(ValueError):
        slicer.parse_date("2021-01-01T00:00:00.000000+0000")


@pytest.mark.parametrize(
    "test_name, input_dt, datetimeformat, datetimeformat_granularity, expected_output",
    [
        ("test_format_timestamp", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%s", "PT1S", "1609459200"),
        ("test_format_string", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%Y-%m-%d", "P1D", "2021-01-01"),
        ("test_format_to_number", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%Y%m%d", "P1D", "20210101"),
    ],
)
def test_format_datetime(test_name, input_dt, datetimeformat, datetimeformat_granularity, expected_output):
    slicer = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2021-01-01T00:00:00.000000+0000", parameters={}),
        end_datetime=MinMaxDatetime("2021-01-10T00:00:00.000000+0000", parameters={}),
        step="P1D",
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format=datetimeformat,
        cursor_granularity=datetimeformat_granularity,
        lookback_window=InterpolatedString("P0D", parameters={}),
        config=config,
        parameters={},
    )

    output_date = slicer._format_datetime(input_dt)
    assert expected_output == output_date


def test_step_but_no_cursor_granularity():
    with pytest.raises(ValueError):
        DatetimeBasedCursor(
            start_datetime=MinMaxDatetime("2021-01-01T00:00:00.000000+0000", parameters={}),
            end_datetime=MinMaxDatetime("2021-01-10T00:00:00.000000+0000", parameters={}),
            step="P1D",
            cursor_field=InterpolatedString(cursor_field, parameters={}),
            datetime_format="%Y-%m-%d",
            config=config,
            parameters={},
        )


def test_cursor_granularity_but_no_step():
    with pytest.raises(ValueError):
        DatetimeBasedCursor(
            start_datetime=MinMaxDatetime("2021-01-01T00:00:00.000000+0000", parameters={}),
            end_datetime=MinMaxDatetime("2021-01-10T00:00:00.000000+0000", parameters={}),
            cursor_granularity="P1D",
            cursor_field=InterpolatedString(cursor_field, parameters={}),
            datetime_format="%Y-%m-%d",
            config=config,
            parameters={},
        )


def test_given_multiple_cursor_datetime_format_then_slice_using_first_format():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2021-01-01", parameters={}),
        end_datetime=MinMaxDatetime("2023-01-10", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        cursor_datetime_formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"],
        config=config,
        parameters={},
    )
    stream_slices = cursor.stream_slices()
    assert stream_slices == [{"start_time": "2021-01-01", "end_time": "2023-01-10"}]


def test_no_cursor_granularity_and_no_step_then_only_return_one_slice():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2021-01-01", parameters={}),
        end_datetime=MinMaxDatetime("2023-01-01", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    stream_slices = cursor.stream_slices()
    assert stream_slices == [{"start_time": "2021-01-01", "end_time": "2023-01-01"}]


def test_no_end_datetime(mock_datetime_now):
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2021-01-01", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    stream_slices = cursor.stream_slices()
    assert stream_slices == [{"start_time": "2021-01-01", "end_time": FAKE_NOW.strftime("%Y-%m-%d")}]


def test_given_no_state_and_start_before_cursor_value_when_should_be_synced_then_return_true():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2021-01-01", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    assert cursor.should_be_synced(Record({cursor_field: "2022-01-01"}, ANY_SLICE))


def test_given_no_state_and_start_after_cursor_value_when_should_be_synced_then_return_false():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2022-01-01", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    assert not cursor.should_be_synced(Record({cursor_field: "2021-01-01"}, ANY_SLICE))


def test_given_state_earliest_to_start_datetime_when_should_be_synced_then_use_state_as_earliest_boundary():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2021-01-01", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    cursor.set_initial_state({cursor_field: "2023-01-01"})
    assert not cursor.should_be_synced(Record({cursor_field: "2022-01-01"}, ANY_SLICE))


def test_given_start_datetime_earliest_to_state_when_should_be_synced_then_use_start_datetime_as_earliest_boundary():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2023-01-01", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    cursor.set_initial_state({cursor_field: "2021-01-01"})
    assert not cursor.should_be_synced(Record({cursor_field: "2022-01-01"}, ANY_SLICE))


def test_given_end_datetime_before_cursor_value_when_should_be_synced_then_return_false():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2023-01-01", parameters={}),
        end_datetime=MinMaxDatetime("2025-01-01", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    assert not cursor.should_be_synced(Record({cursor_field: "2030-01-01"}, ANY_SLICE))


def test_given_record_without_cursor_value_when_should_be_synced_then_return_true():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("3000-01-01", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    assert cursor.should_be_synced(Record({"record without cursor value": "any"}, ANY_SLICE))


def test_given_first_greater_than_second_then_return_true():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("3000-01-01", parameters={}),
        cursor_field="cursor_field",
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    assert cursor.is_greater_than_or_equal(Record({"cursor_field": "2023-01-01"}, {}), Record({"cursor_field": "2021-01-01"}, {}))


def test_given_first_lesser_than_second_then_return_false():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("3000-01-01", parameters={}),
        cursor_field="cursor_field",
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    assert not cursor.is_greater_than_or_equal(Record({"cursor_field": "2021-01-01"}, {}), Record({"cursor_field": "2023-01-01"}, {}))


def test_given_no_cursor_value_for_second_than_second_then_return_true():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("3000-01-01", parameters={}),
        cursor_field="cursor_field",
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    assert cursor.is_greater_than_or_equal(Record({"cursor_field": "2021-01-01"}, {}), Record({}, {}))


def test_given_no_cursor_value_for_first_than_second_then_return_false():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("3000-01-01", parameters={}),
        cursor_field="cursor_field",
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    assert not cursor.is_greater_than_or_equal(Record({}, {}), Record({"cursor_field": "2021-01-01"}, {}))


if __name__ == "__main__":
    unittest.main()
