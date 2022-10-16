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
end_date_now = InterpolatedString(string="{{ today_utc() }}", options={})
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
            MinMaxDatetime(datetime="{{ config['start_date'] }}", options={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-01T00:00:00.000000+0000"},
                {"start_time": "2021-01-02T00:00:00.000000+0000", "end_time": "2021-01-02T00:00:00.000000+0000"},
                {"start_time": "2021-01-03T00:00:00.000000+0000", "end_time": "2021-01-03T00:00:00.000000+0000"},
                {"start_time": "2021-01-04T00:00:00.000000+0000", "end_time": "2021-01-04T00:00:00.000000+0000"},
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
                {"start_time": "2021-01-06T00:00:00.000000+0000", "end_time": "2021-01-06T00:00:00.000000+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-07T00:00:00.000000+0000"},
                {"start_time": "2021-01-08T00:00:00.000000+0000", "end_time": "2021-01-08T00:00:00.000000+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-09T00:00:00.000000+0000"},
                {"start_time": "2021-01-10T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_2_day",
            None,
            MinMaxDatetime(datetime="{{ config['start_date'] }}", options={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
            "2d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-02T00:00:00.000000+0000"},
                {"start_time": "2021-01-03T00:00:00.000000+0000", "end_time": "2021-01-04T00:00:00.000000+0000"},
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-06T00:00:00.000000+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-08T00:00:00.000000+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_from_stream_state",
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="{{ stream_state['date'] }}", options={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
                {"start_time": "2021-01-06T00:00:00.000000+0000", "end_time": "2021-01-06T00:00:00.000000+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-07T00:00:00.000000+0000"},
                {"start_time": "2021-01-08T00:00:00.000000+0000", "end_time": "2021-01-08T00:00:00.000000+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-09T00:00:00.000000+0000"},
                {"start_time": "2021-01-10T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_12_day",
            None,
            MinMaxDatetime(datetime="{{ config['start_date'] }}", options={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
            "12d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_end_time_greater_than_now",
            None,
            MinMaxDatetime(datetime="2021-12-28T00:00:00.000000+0000", options={}),
            MinMaxDatetime(datetime=f"{(FAKE_NOW + datetime.timedelta(days=1)).strftime(datetime_format)}", options={}),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_time": "2021-12-28T00:00:00.000000+0000", "end_time": "2021-12-28T00:00:00.000000+0000"},
                {"start_time": "2021-12-29T00:00:00.000000+0000", "end_time": "2021-12-29T00:00:00.000000+0000"},
                {"start_time": "2021-12-30T00:00:00.000000+0000", "end_time": "2021-12-30T00:00:00.000000+0000"},
                {"start_time": "2021-12-31T00:00:00.000000+0000", "end_time": "2021-12-31T00:00:00.000000+0000"},
                {"start_time": "2022-01-01T00:00:00.000000+0000", "end_time": "2022-01-01T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_start_date_greater_than_end_time",
            None,
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
            MinMaxDatetime(datetime="2021-01-05T00:00:00.000000+0000", options={}),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_cursor_date_greater_than_start_date",
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="{{ stream_state['date'] }}", options={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
            "1d",
            InterpolatedString(string="{{ stream_state['date'] }}", options={}),
            None,
            datetime_format,
            [
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
                {"start_time": "2021-01-06T00:00:00.000000+0000", "end_time": "2021-01-06T00:00:00.000000+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-07T00:00:00.000000+0000"},
                {"start_time": "2021-01-08T00:00:00.000000+0000", "end_time": "2021-01-08T00:00:00.000000+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-09T00:00:00.000000+0000"},
                {"start_time": "2021-01-10T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_cursor_date_greater_than_start_date_multiday_step",
            {cursor_field: "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="2021-01-03T00:00:00.000000+0000", options={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
            "2d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_time": "2021-01-06T00:00:00.000000+0000", "end_time": "2021-01-07T00:00:00.000000+0000"},
                {"start_time": "2021-01-08T00:00:00.000000+0000", "end_time": "2021-01-09T00:00:00.000000+0000"},
                {"start_time": "2021-01-10T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_start_date_less_than_min_date",
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="{{ config['start_date'] }}", min_datetime="{{ stream_state['date'] }}", options={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
            "1d",
            InterpolatedString(string="{{ stream_state['date'] }}", options={}),
            None,
            datetime_format,
            [
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
                {"start_time": "2021-01-06T00:00:00.000000+0000", "end_time": "2021-01-06T00:00:00.000000+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-07T00:00:00.000000+0000"},
                {"start_time": "2021-01-08T00:00:00.000000+0000", "end_time": "2021-01-08T00:00:00.000000+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-09T00:00:00.000000+0000"},
                {"start_time": "2021-01-10T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_end_date_greater_than_max_date",
            {"date": "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="{{ config['start_date'] }}", options={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", max_datetime="{{ stream_state['date'] }}", options={}),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-01T00:00:00.000000+0000"},
                {"start_time": "2021-01-02T00:00:00.000000+0000", "end_time": "2021-01-02T00:00:00.000000+0000"},
                {"start_time": "2021-01-03T00:00:00.000000+0000", "end_time": "2021-01-03T00:00:00.000000+0000"},
                {"start_time": "2021-01-04T00:00:00.000000+0000", "end_time": "2021-01-04T00:00:00.000000+0000"},
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_start_end_min_max_inherits_datetime_format_from_stream_slicer",
            {"date": "2021-01-05"},
            MinMaxDatetime(datetime="{{ config['start_date_ymd'] }}", options={}),
            MinMaxDatetime(datetime="2021-01-10", max_datetime="{{ stream_state['date'] }}", options={}),
            "1d",
            cursor_field,
            None,
            "%Y-%m-%d",
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
            MinMaxDatetime(datetime="{{ config['start_date'] }}", options={}),
            MinMaxDatetime(datetime="2021-01-10", max_datetime="{{ stream_state['date'] }}", datetime_format="%Y-%m-%d", options={}),
            "1d",
            cursor_field,
            "3d",
            datetime_format,
            [
                {"start_time": "2020-12-29T00:00:00.000000+0000", "end_time": "2020-12-29T00:00:00.000000+0000"},
                {"start_time": "2020-12-30T00:00:00.000000+0000", "end_time": "2020-12-30T00:00:00.000000+0000"},
                {"start_time": "2020-12-31T00:00:00.000000+0000", "end_time": "2020-12-31T00:00:00.000000+0000"},
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-01T00:00:00.000000+0000"},
                {"start_time": "2021-01-02T00:00:00.000000+0000", "end_time": "2021-01-02T00:00:00.000000+0000"},
                {"start_time": "2021-01-03T00:00:00.000000+0000", "end_time": "2021-01-03T00:00:00.000000+0000"},
                {"start_time": "2021-01-04T00:00:00.000000+0000", "end_time": "2021-01-04T00:00:00.000000+0000"},
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_with_lookback_window_defaults_to_0d",
            {"date": "2021-01-05"},
            MinMaxDatetime(datetime="{{ config['start_date'] }}", options={}),
            MinMaxDatetime(datetime="2021-01-10", max_datetime="{{ stream_state['date'] }}", datetime_format="%Y-%m-%d", options={}),
            "1d",
            cursor_field,
            "{{ config['does_not_exist'] }}",
            datetime_format,
            [
                {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-01T00:00:00.000000+0000"},
                {"start_time": "2021-01-02T00:00:00.000000+0000", "end_time": "2021-01-02T00:00:00.000000+0000"},
                {"start_time": "2021-01-03T00:00:00.000000+0000", "end_time": "2021-01-03T00:00:00.000000+0000"},
                {"start_time": "2021-01-04T00:00:00.000000+0000", "end_time": "2021-01-04T00:00:00.000000+0000"},
                {"start_time": "2021-01-05T00:00:00.000000+0000", "end_time": "2021-01-05T00:00:00.000000+0000"},
            ],
        ),
        (
            "test_start_is_after_stream_state",
            {cursor_field: "2021-01-05T00:00:00.000000+0000"},
            MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", options={}),
            MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
            "1d",
            cursor_field,
            None,
            datetime_format,
            [
                {"start_time": "2021-01-06T00:00:00.000000+0000", "end_time": "2021-01-06T00:00:00.000000+0000"},
                {"start_time": "2021-01-07T00:00:00.000000+0000", "end_time": "2021-01-07T00:00:00.000000+0000"},
                {"start_time": "2021-01-08T00:00:00.000000+0000", "end_time": "2021-01-08T00:00:00.000000+0000"},
                {"start_time": "2021-01-09T00:00:00.000000+0000", "end_time": "2021-01-09T00:00:00.000000+0000"},
                {"start_time": "2021-01-10T00:00:00.000000+0000", "end_time": "2021-01-10T00:00:00.000000+0000"},
            ],
        ),
    ],
)
def test_stream_slices(
    mock_datetime_now, test_name, stream_state, start, end, step, cursor_field, lookback_window, datetime_format, expected_slices
):
    lookback_window = InterpolatedString(string=lookback_window, options={}) if lookback_window else None
    slicer = DatetimeStreamSlicer(
        start_datetime=start,
        end_datetime=end,
        step=step,
        cursor_field=cursor_field,
        datetime_format=datetime_format,
        lookback_window=lookback_window,
        config=config,
        options={},
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
        start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", options={}),
        end_datetime=MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
        step="1d",
        cursor_field=InterpolatedString(string=cursor_field, options={}),
        datetime_format=datetime_format,
        lookback_window=InterpolatedString(string="0d", options={}),
        config=config,
        options={},
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
        (
            "test_start_time_inject_into_path",
            RequestOptionType.path,
            "start_time",
            {},
            {},
            {},
            {"start_time": "2021-01-01T00:00:00.000000+0000", "endtime": "2021-01-04T00:00:00.000000+0000"},
        ),
    ],
)
def test_request_option(test_name, inject_into, field_name, expected_req_params, expected_headers, expected_body_json, expected_body_data):
    if inject_into == RequestOptionType.path:
        start_request_option = RequestOption(inject_into=inject_into, options={})
        end_request_option = RequestOption(inject_into=inject_into, options={})
        try:
            DatetimeStreamSlicer(
                start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", options={}),
                end_datetime=MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
                step="1d",
                cursor_field=InterpolatedString(string=cursor_field, options={}),
                datetime_format=datetime_format,
                lookback_window=InterpolatedString(string="0d", options={}),
                start_time_option=start_request_option,
                end_time_option=end_request_option,
                config=config,
                options={},
            )
            assert False
        except ValueError:
            return
    else:
        start_request_option = RequestOption(inject_into=inject_into, options={}, field_name=field_name) if inject_into else None
        end_request_option = RequestOption(inject_into=inject_into, options={}, field_name="endtime") if inject_into else None
        slicer = DatetimeStreamSlicer(
            start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", options={}),
            end_datetime=MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", options={}),
            step="1d",
            cursor_field=InterpolatedString(string=cursor_field, options={}),
            datetime_format=datetime_format,
            lookback_window=InterpolatedString(string="0d", options={}),
            start_time_option=start_request_option,
            end_time_option=end_request_option,
            config=config,
            options={},
        )
    stream_slice = {"start_time": "2021-01-01T00:00:00.000000+0000", "end_time": "2021-01-04T00:00:00.000000+0000"}

    slicer.update_cursor(stream_slice)

    assert expected_req_params == slicer.get_request_params(stream_slice=stream_slice)
    assert expected_headers == slicer.get_request_headers(stream_slice=stream_slice)
    assert expected_body_json == slicer.get_request_body_json(stream_slice=stream_slice)
    assert expected_body_data == slicer.get_request_body_data(stream_slice=stream_slice)


@pytest.mark.parametrize(
    "test_name, input_date, date_format, expected_output_date",
    [
        (
            "test_parse_date_iso",
            "2021-01-01T00:00:00.000000+0000",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        (
            "test_parse_timestamp",
            "1609459200",
            "%s",
            datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        ),
        ("test_parse_date_number", "20210101", "%Y%m%d", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)),
    ],
)
def test_parse_date(test_name, input_date, date_format, expected_output_date):
    slicer = DatetimeStreamSlicer(
        start_datetime=MinMaxDatetime("2021-01-01T00:00:00.000000+0000", options={}),
        end_datetime=MinMaxDatetime("2021-01-10T00:00:00.000000+0000", options={}),
        step="1d",
        cursor_field=InterpolatedString(cursor_field, options={}),
        datetime_format=date_format,
        lookback_window=InterpolatedString("0d", options={}),
        config=config,
        options={},
    )
    output_date = slicer.parse_date(input_date)
    assert expected_output_date == output_date


@pytest.mark.parametrize(
    "test_name, input_dt, datetimeformat, expected_output",
    [
        ("test_format_timestamp", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%s", "1609459200"),
        ("test_format_string", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%Y-%m-%d", "2021-01-01"),
        ("test_format_to_number", datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), "%Y%m%d", "20210101"),
    ],
)
def test_format_datetime(test_name, input_dt, datetimeformat, expected_output):
    slicer = DatetimeStreamSlicer(
        start_datetime=MinMaxDatetime("2021-01-01T00:00:00.000000+0000", options={}),
        end_datetime=MinMaxDatetime("2021-01-10T00:00:00.000000+0000", options={}),
        step="1d",
        cursor_field=InterpolatedString(cursor_field, options={}),
        datetime_format=datetimeformat,
        lookback_window=InterpolatedString("0d", options={}),
        config=config,
        options={},
    )

    output_date = slicer._format_datetime(input_dt)
    assert expected_output == output_date


if __name__ == "__main__":
    unittest.main()
