#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import unittest

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType

datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
cursor_granularity = "PT0.000001S"
FAKE_NOW = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)

config = {"start_date": "2021-01-01T00:00:00.000000+0000", "start_date_ymd": "2021-01-01"}
end_date_now = InterpolatedString(string="{{ today_utc() }}", parameters={})
cursor_field = "created"
timezone = datetime.timezone.utc


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
            None,
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
            None,
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
            None,
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
            None,
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
            None,
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
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="{{ stream_state['date'] }}", parameters={}),
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
            None,
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
            None,
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
            None,
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
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="{{ stream_state['date'] }}", parameters={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
            "P1D",
            InterpolatedString(string="{{ stream_state['date'] }}", parameters={}),
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
            "test_start_date_less_than_min_date",
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="{{ config['start_date'] }}", min_datetime="{{ stream_state['date'] }}", parameters={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
            "P1D",
            InterpolatedString(string="{{ stream_state['date'] }}", parameters={}),
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
            "test_end_date_greater_than_max_date",
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="{{ config['start_date'] }}", parameters={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", max_datetime="{{ stream_state['date'] }}", parameters={}),
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
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_start_end_min_max_inherits_datetime_format_from_stream_slicer",
            {"date": "2021-01-05"},
            MinMaxDatetime(datetime="{{ config['start_date_ymd'] }}", parameters={}),
            MinMaxDatetime(datetime="2021-01-10", max_datetime="{{ stream_state['date'] }}", parameters={}),
            "P1D",
            cursor_field,
            None,
            "%Y-%m-%d",
            "P1D",
            [
                {"start_time": "2021-01-01", "end_time": "2021-01-01"},
                {"start_time": "2021-01-02", "end_time": "2021-01-02"},
                {"start_time": "2021-01-03", "end_time": "2021-01-03"},
                {"start_time": "2021-01-04", "end_time": "2021-01-04"},
                {"start_time": "2021-01-05", "end_time": "2021-01-05"},
            ],
        ),
        (
            "test_with_lookback_window_from_start_date",
            {"date": "2021-01-05"},
            MinMaxDatetime(datetime="{{ config['start_date'] }}", parameters={}),
            MinMaxDatetime(datetime="2021-01-10", max_datetime="{{ stream_state['date'] }}", datetime_format="%Y-%m-%d", parameters={}),
            "P1D",
            cursor_field,
            "P3D",
            datetime_format,
            cursor_granularity,
            [
                {"start_time": "2020-12-29T00:00:00.000000+0000", "end_time": "2020-12-29T23:59:59.999999+0000"},
                {"start_time": "2020-12-30T00:00:00.000000+0000", "end_time": "2020-12-30T23:59:59.999999+0000"},
                {"start_time": "2020-12-31T00:00:00.000000+0000", "end_time": "2020-12-31T23:59:59.999999+0000"},
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-01T23:59:59.999999+0000"},
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
            {"date": "2021-01-05"},
            MinMaxDatetime(datetime="{{ config['start_date'] }}", parameters={}),
            MinMaxDatetime(datetime="2021-01-10", max_datetime="{{ stream_state['date'] }}", datetime_format="%Y-%m-%d", parameters={}),
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
    slicer = DatetimeBasedCursor(
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
    stream_slices = slicer.stream_slices(SyncMode.incremental, stream_state)

    assert stream_slices == expected_slices


@pytest.mark.parametrize(
    "test_name, previous_cursor, stream_slice, last_record, expected_state",
    [
        ("test_update_cursor_no_state_no_record", None, {}, None, {}),
        (
            "test_update_cursor_with_state_no_record",
            None,
            {cursor_field: "2021-01-02T00:00:00.000000+0000"},
            None,
            {cursor_field: "2021-01-02T00:00:00.000000+0000"},
        ),
        (
            "test_update_cursor_with_state_equals_record",
            None,
            {cursor_field: "2021-01-02T00:00:00.000000+0000"},
            {cursor_field: "2021-01-02T00:00:00.000000+0000"},
            {cursor_field: "2021-01-02T00:00:00.000000+0000"},
        ),
        (
            "test_update_cursor_with_state_greater_than_record",
            None,
            {cursor_field: "2021-01-03T00:00:00.000000+0000"},
            {cursor_field: "2021-01-02T00:00:00.000000+0000"},
            {cursor_field: "2021-01-03T00:00:00.000000+0000"},
        ),
        (
            "test_update_cursor_with_state_less_than_record",
            None,
            {cursor_field: "2021-01-02T00:00:00.000000+0000"},
            {cursor_field: "2021-01-03T00:00:00.000000+0000"},
            {cursor_field: "2021-01-03T00:00:00.000000+0000"},
        ),
        (
            "test_update_cursor_with_state_less_than_previous_cursor",
            "2021-01-03T00:00:00.000000+0000",
            {cursor_field: "2021-01-02T00:00:00.000000+0000"},
            {},
            {cursor_field: "2021-01-03T00:00:00.000000+0000"},
        ),
    ],
)
def test_update_cursor(test_name, previous_cursor, stream_slice, last_record, expected_state):
    slicer = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", parameters={}),
        end_datetime=MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
        step="P1D",
        cursor_field=InterpolatedString(string=cursor_field, parameters={}),
        datetime_format=datetime_format,
        cursor_granularity=cursor_granularity,
        lookback_window=InterpolatedString(string="0d", parameters={}),
        config=config,
        parameters={},
    )
    slicer._cursor = previous_cursor
    slicer.update_cursor(stream_slice, last_record)
    updated_state = slicer.get_stream_state()
    assert expected_state == updated_state


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

    slicer.update_cursor(stream_slice)

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
def test_parse_date(test_name, input_date, date_format, date_format_granularity, expected_output_date):
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


def test_no_cursor_granularity_and_no_step_then_only_return_one_slice():
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2021-01-01", parameters={}),
        end_datetime=MinMaxDatetime("2023-01-01", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    stream_slices = cursor.stream_slices(SyncMode.incremental, {})
    assert stream_slices == [{"start_time": "2021-01-01", "end_time": "2023-01-01"}]


def test_no_end_datetime(mock_datetime_now):
    cursor = DatetimeBasedCursor(
        start_datetime=MinMaxDatetime("2021-01-01", parameters={}),
        cursor_field=InterpolatedString(cursor_field, parameters={}),
        datetime_format="%Y-%m-%d",
        config=config,
        parameters={},
    )
    stream_slices = cursor.stream_slices(SyncMode.incremental, {})
    assert stream_slices == [{"start_time": "2021-01-01", "end_time": FAKE_NOW.strftime("%Y-%m-%d")}]


if __name__ == "__main__":
    unittest.main()
