#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import unittest

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer

datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
FAKE_NOW = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)

config = {"start_date": "2021-01-01T00:00:00.000000+0000", "start_date_ymd": "2021-01-01"}
end_date_now = InterpolatedString(
    "{{ today_utc() }}",
)
cursor_field = "created"
timezone = datetime.timezone.utc


@pytest.fixture()
def mock_datetime_now(monkeypatch):
    datetime_mock = unittest.mock.MagicMock(wraps=datetime.datetime)
    datetime_mock.now.return_value = FAKE_NOW
    monkeypatch.setattr(datetime, "datetime", datetime_mock)


@pytest.mark.parametrize(
    "test_name, stream_state, start, end, step, cursor_field, lookback_window, datetime_format, expected_slices",
    [
        (
            "test_1_day",
            None,
            MinMaxDatetime("{{ config['start_date'] }}"),
            MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_date": "2021-01-01T00:00:00.000000+0000", "end_date": "2021-01-01T00:00:00.000000+0000"},
                {"start_date": "2021-01-02T00:00:00.000000+0000", "end_date": "2021-01-02T00:00:00.000000+0000"},
                {"start_date": "2021-01-03T00:00:00.000000+0000", "end_date": "2021-01-03T00:00:00.000000+0000"},
                {"start_date": "2021-01-04T00:00:00.000000+0000", "end_date": "2021-01-04T00:00:00.000000+0000"},
                {"start_date": "2021-01-05T00:00:00.000000+0000", "end_date": "2021-01-05T00:00:00.000000+0000"},
                {"start_date": "2021-01-06T00:00:00.000000+0000", "end_date": "2021-01-06T00:00:00.000000+0000"},
                {"start_date": "2021-01-07T00:00:00.000000+0000", "end_date": "2021-01-07T00:00:00.000000+0000"},
                {"start_date": "2021-01-08T00:00:00.000000+0000", "end_date": "2021-01-08T00:00:00.000000+0000"},
                {"start_date": "2021-01-09T00:00:00.000000+0000", "end_date": "2021-01-09T00:00:00.000000+0000"},
                {"start_date": "2021-01-10T00:00:00.000000+0000", "end_date": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_2_day",
            None,
            MinMaxDatetime("{{ config['start_date'] }}"),
            MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
            "2d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_date": "2021-01-01T00:00:00.000000+0000", "end_date": "2021-01-02T00:00:00.000000+0000"},
                {"start_date": "2021-01-03T00:00:00.000000+0000", "end_date": "2021-01-04T00:00:00.000000+0000"},
                {"start_date": "2021-01-05T00:00:00.000000+0000", "end_date": "2021-01-06T00:00:00.000000+0000"},
                {"start_date": "2021-01-07T00:00:00.000000+0000", "end_date": "2021-01-08T00:00:00.000000+0000"},
                {"start_date": "2021-01-09T00:00:00.000000+0000", "end_date": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_from_stream_state",
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime("{{ stream_state['date'] }}"),
            MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_date": "2021-01-05T00:00:00.000000+0000", "end_date": "2021-01-05T00:00:00.000000+0000"},
                {"start_date": "2021-01-06T00:00:00.000000+0000", "end_date": "2021-01-06T00:00:00.000000+0000"},
                {"start_date": "2021-01-07T00:00:00.000000+0000", "end_date": "2021-01-07T00:00:00.000000+0000"},
                {"start_date": "2021-01-08T00:00:00.000000+0000", "end_date": "2021-01-08T00:00:00.000000+0000"},
                {"start_date": "2021-01-09T00:00:00.000000+0000", "end_date": "2021-01-09T00:00:00.000000+0000"},
                {"start_date": "2021-01-10T00:00:00.000000+0000", "end_date": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_12_day",
            None,
            MinMaxDatetime("{{ config['start_date'] }}"),
            MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
            "12d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_date": "2021-01-01T00:00:00.000000+0000", "end_date": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_end_date_greater_than_now",
            None,
            MinMaxDatetime("2021-12-28T00:00:00.000000+0000"),
            MinMaxDatetime(f"{(FAKE_NOW + datetime.timedelta(days=1)).strftime(datetime_format)}"),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_date": "2021-12-28T00:00:00.000000+0000", "end_date": "2021-12-28T00:00:00.000000+0000"},
                {"start_date": "2021-12-29T00:00:00.000000+0000", "end_date": "2021-12-29T00:00:00.000000+0000"},
                {"start_date": "2021-12-30T00:00:00.000000+0000", "end_date": "2021-12-30T00:00:00.000000+0000"},
                {"start_date": "2021-12-31T00:00:00.000000+0000", "end_date": "2021-12-31T00:00:00.000000+0000"},
                {"start_date": "2022-01-01T00:00:00.000000+0000", "end_date": "2022-01-01T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_start_date_greater_than_end_date",
            None,
            MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
            MinMaxDatetime("2021-01-05T00:00:00.000000+0000"),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_date": "2021-01-05T00:00:00.000000+0000", "end_date": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_cursor_date_greater_than_start_date",
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime("{{ stream_state['date'] }}"),
            MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
            "1d",
            InterpolatedString("{{ stream_state['date'] }}"),
            None,
            datetime_format,
            [
                {"start_date": "2021-01-05T00:00:00.000000+0000", "end_date": "2021-01-05T00:00:00.000000+0000"},
                {"start_date": "2021-01-06T00:00:00.000000+0000", "end_date": "2021-01-06T00:00:00.000000+0000"},
                {"start_date": "2021-01-07T00:00:00.000000+0000", "end_date": "2021-01-07T00:00:00.000000+0000"},
                {"start_date": "2021-01-08T00:00:00.000000+0000", "end_date": "2021-01-08T00:00:00.000000+0000"},
                {"start_date": "2021-01-09T00:00:00.000000+0000", "end_date": "2021-01-09T00:00:00.000000+0000"},
                {"start_date": "2021-01-10T00:00:00.000000+0000", "end_date": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_cursor_date_greater_than_start_date_multiday_step",
            {cursor_field: "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime("2021-01-03T00:00:00.000000+0000"),
            MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
            "2d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_date": "2021-01-06T00:00:00.000000+0000", "end_date": "2021-01-07T00:00:00.000000+0000"},
                {"start_date": "2021-01-08T00:00:00.000000+0000", "end_date": "2021-01-09T00:00:00.000000+0000"},
                {"start_date": "2021-01-10T00:00:00.000000+0000", "end_date": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_start_date_less_than_min_date",
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime("{{ config['start_date'] }}", min_datetime="{{ stream_state['date'] }}"),
            MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
            "1d",
            InterpolatedString("{{ stream_state['date'] }}"),
            None,
            datetime_format,
            [
                {"start_date": "2021-01-05T00:00:00.000000+0000", "end_date": "2021-01-05T00:00:00.000000+0000"},
                {"start_date": "2021-01-06T00:00:00.000000+0000", "end_date": "2021-01-06T00:00:00.000000+0000"},
                {"start_date": "2021-01-07T00:00:00.000000+0000", "end_date": "2021-01-07T00:00:00.000000+0000"},
                {"start_date": "2021-01-08T00:00:00.000000+0000", "end_date": "2021-01-08T00:00:00.000000+0000"},
                {"start_date": "2021-01-09T00:00:00.000000+0000", "end_date": "2021-01-09T00:00:00.000000+0000"},
                {"start_date": "2021-01-10T00:00:00.000000+0000", "end_date": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_end_date_greater_than_max_date",
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime("{{ config['start_date'] }}"),
            MinMaxDatetime("2021-01-10T00:00:00.000000+0000", max_datetime="{{ stream_state['date'] }}"),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_date": "2021-01-01T00:00:00.000000+0000", "end_date": "2021-01-01T00:00:00.000000+0000"},
                {"start_date": "2021-01-02T00:00:00.000000+0000", "end_date": "2021-01-02T00:00:00.000000+0000"},
                {"start_date": "2021-01-03T00:00:00.000000+0000", "end_date": "2021-01-03T00:00:00.000000+0000"},
                {"start_date": "2021-01-04T00:00:00.000000+0000", "end_date": "2021-01-04T00:00:00.000000+0000"},
                {"start_date": "2021-01-05T00:00:00.000000+0000", "end_date": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_start_end_min_max_inherits_datetime_format_from_stream_slicer",
            {"date": "2021-01-05"},
            MinMaxDatetime("{{ config['start_date_ymd'] }}"),
            MinMaxDatetime("2021-01-10", max_datetime="{{ stream_state['date'] }}"),
            "1d",
            cursor_field,
            None,
            "%Y-%m-%d",
            [
                {"start_date": "2021-01-01", "end_date": "2021-01-01"},
                {"start_date": "2021-01-02", "end_date": "2021-01-02"},
                {"start_date": "2021-01-03", "end_date": "2021-01-03"},
                {"start_date": "2021-01-04", "end_date": "2021-01-04"},
                {"start_date": "2021-01-05", "end_date": "2021-01-05"},
            ],
        ),
        (
            "test_with_lookback_window_from_start_date",
            {"date": "2021-01-05"},
            MinMaxDatetime("{{ config['start_date'] }}"),
            MinMaxDatetime("2021-01-10", max_datetime="{{ stream_state['date'] }}", datetime_format="%Y-%m-%d"),
            "1d",
            cursor_field,
            "3d",
            datetime_format,
            [
                {"start_date": "2020-12-29T00:00:00.000000+0000", "end_date": "2020-12-29T00:00:00.000000+0000"},
                {"start_date": "2020-12-30T00:00:00.000000+0000", "end_date": "2020-12-30T00:00:00.000000+0000"},
                {"start_date": "2020-12-31T00:00:00.000000+0000", "end_date": "2020-12-31T00:00:00.000000+0000"},
                {"start_date": "2021-01-01T00:00:00.000000+0000", "end_date": "2021-01-01T00:00:00.000000+0000"},
                {"start_date": "2021-01-02T00:00:00.000000+0000", "end_date": "2021-01-02T00:00:00.000000+0000"},
                {"start_date": "2021-01-03T00:00:00.000000+0000", "end_date": "2021-01-03T00:00:00.000000+0000"},
                {"start_date": "2021-01-04T00:00:00.000000+0000", "end_date": "2021-01-04T00:00:00.000000+0000"},
                {"start_date": "2021-01-05T00:00:00.000000+0000", "end_date": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_with_lookback_window_defaults_to_0d",
            {"date": "2021-01-05"},
            MinMaxDatetime("{{ config['start_date'] }}"),
            MinMaxDatetime("2021-01-10", max_datetime="{{ stream_state['date'] }}", datetime_format="%Y-%m-%d"),
            "1d",
            cursor_field,
            "{{ config['does_not_exist'] }}",
            datetime_format,
            [
                {"start_date": "2021-01-01T00:00:00.000000+0000", "end_date": "2021-01-01T00:00:00.000000+0000"},
                {"start_date": "2021-01-02T00:00:00.000000+0000", "end_date": "2021-01-02T00:00:00.000000+0000"},
                {"start_date": "2021-01-03T00:00:00.000000+0000", "end_date": "2021-01-03T00:00:00.000000+0000"},
                {"start_date": "2021-01-04T00:00:00.000000+0000", "end_date": "2021-01-04T00:00:00.000000+0000"},
                {"start_date": "2021-01-05T00:00:00.000000+0000", "end_date": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_start_is_after_stream_state",
            {cursor_field: "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime("2021-01-01T00:00:00.000000+0000"),
            MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_date": "2021-01-06T00:00:00.000000+0000", "end_date": "2021-01-06T00:00:00.000000+0000"},
                {"start_date": "2021-01-07T00:00:00.000000+0000", "end_date": "2021-01-07T00:00:00.000000+0000"},
                {"start_date": "2021-01-08T00:00:00.000000+0000", "end_date": "2021-01-08T00:00:00.000000+0000"},
                {"start_date": "2021-01-09T00:00:00.000000+0000", "end_date": "2021-01-09T00:00:00.000000+0000"},
                {"start_date": "2021-01-10T00:00:00.000000+0000", "end_date": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
    ],
)
def test_stream_slices(
    mock_datetime_now, test_name, stream_state, start, end, step, cursor_field, lookback_window, datetime_format, expected_slices
):
    lookback_window = InterpolatedString(lookback_window) if lookback_window else None
    slicer = DatetimeStreamSlicer(
        start_datetime=start,
        end_datetime=end,
        step=step,
        cursor_field=cursor_field,
        datetime_format=datetime_format,
        lookback_window=lookback_window,
        config=config,
    )
    stream_slices = slicer.stream_slices(SyncMode.incremental, stream_state)

    assert expected_slices == stream_slices


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
    slicer = DatetimeStreamSlicer(
        start_datetime=MinMaxDatetime("2021-01-01T00:00:00.000000+0000"),
        end_datetime=MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
        step="1d",
        cursor_field=InterpolatedString(cursor_field),
        datetime_format=datetime_format,
        lookback_window=InterpolatedString("0d"),
        config=config,
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
            {"start_time": "2021-01-02T00:00:00.000000+0000", "endtime": "2021-01-04T00:00:00.000000+0000"},
            {},
            {},
            {},
        ),
        (
            "test_start_time_inject_into_header",
            RequestOptionType.header,
            "start_time",
            {},
            {"start_time": "2021-01-02T00:00:00.000000+0000", "endtime": "2021-01-04T00:00:00.000000+0000"},
            {},
            {},
        ),
        (
            "test_start_time_inject_intoy_body_json",
            RequestOptionType.body_json,
            "start_time",
            {},
            {},
            {"start_time": "2021-01-02T00:00:00.000000+0000", "endtime": "2021-01-04T00:00:00.000000+0000"},
            {},
        ),
        (
            "test_start_time_inject_into_body_data",
            RequestOptionType.body_data,
            "start_time",
            {},
            {},
            {},
            {"start_time": "2021-01-02T00:00:00.000000+0000", "endtime": "2021-01-04T00:00:00.000000+0000"},
        ),
        (
            "test_start_time_inject_into_path",
            RequestOptionType.path,
            "start_time",
            {},
            {},
            {},
            {"start_time": "2021-01-02T00:00:00.000000+0000", "endtime": "2021-01-04T00:00:00.000000+0000"},
        ),
    ],
)
def test_request_option(test_name, inject_into, field_name, expected_req_params, expected_headers, expected_body_json, expected_body_data):
    if inject_into == RequestOptionType.path:
        start_request_option = RequestOption(inject_into)
        end_request_option = RequestOption(inject_into)
        try:
            DatetimeStreamSlicer(
                start_datetime=MinMaxDatetime("2021-01-01T00:00:00.000000+0000"),
                end_datetime=MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
                step="1d",
                cursor_field=InterpolatedString(cursor_field),
                datetime_format=datetime_format,
                lookback_window=InterpolatedString("0d"),
                start_time_option=start_request_option,
                end_time_option=end_request_option,
                config=config,
            )
            assert False
        except ValueError:
            return
    else:
        start_request_option = RequestOption(inject_into, field_name) if inject_into else None
        end_request_option = RequestOption(inject_into, "endtime") if inject_into else None
        slicer = DatetimeStreamSlicer(
            start_datetime=MinMaxDatetime("2021-01-01T00:00:00.000000+0000"),
            end_datetime=MinMaxDatetime("2021-01-10T00:00:00.000000+0000"),
            step="1d",
            cursor_field=InterpolatedString(cursor_field),
            datetime_format=datetime_format,
            lookback_window=InterpolatedString("0d"),
            start_time_option=start_request_option,
            end_time_option=end_request_option,
            config=config,
        )
    stream_slice = {cursor_field: "2021-01-02T00:00:00.000000+0000", "end_date": "2021-01-04T00:00:00.000000+0000"}

    slicer.update_cursor(stream_slice)

    assert expected_req_params == slicer.request_params()
    assert expected_headers == slicer.request_headers()
    assert expected_body_json == slicer.request_body_json()
    assert expected_body_data == slicer.request_body_data()


if __name__ == "__main__":
    unittest.main()
