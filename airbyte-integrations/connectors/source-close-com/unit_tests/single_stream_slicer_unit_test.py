#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType

from source_close_com.single_stream_slicer import SingleStreamSlicer


def test_update_cursor_compare_stream_slice_and_last_record_and_existing_cursor(mocker):
    slicer = SingleStreamSlicer(
        options=mocker.MagicMock(),
        config=mocker.MagicMock(),
        cursor_field="test_cursor_field",
        start_datetime="2022-01-01",
        datetime_format="%Y-%m-%d"
    )

    setattr(slicer, '_cursor', '2021-01-01T00:00:00Z')

    slicer.update_cursor(
        stream_slice={"test_cursor_field": "2021-01-01T00:00:01Z"},
        last_record={"test_cursor_field": "2021-01-01T00:00:02Z"}
    )
    assert getattr(slicer, '_cursor') == "2021-01-01T00:00:02Z"


def test_get_stream_state(mocker):
    slicer = SingleStreamSlicer(
        options=mocker.MagicMock(),
        config=mocker.MagicMock(),
        cursor_field="test_cursor_field",
        start_datetime="2022-01-01",
        datetime_format="%Y-%m-%d"
    )
    setattr(slicer, '_cursor', '2021-01-01T00:00:00Z')
    assert slicer.get_stream_state() == {'test_cursor_field': '2021-01-01T00:00:00Z'}


def test_get_request_params(mocker):
    request_option = RequestOption(
        field_name="request_field_name",
        inject_into=RequestOptionType.request_parameter,
        options=mocker.MagicMock()
    )
    slicer = SingleStreamSlicer(
        options=mocker.MagicMock(),
        config=mocker.MagicMock(),
        cursor_field="test_cursor_field",
        start_datetime="2022-01-01",
        datetime_format="%Y-%m-%d",
        start_time_option=request_option
    )
    assert slicer.get_request_params(
        stream_state=mocker.MagicMock(),
        stream_slice={"start_time": '2021-01-01T00:00:00Z'}
    ) == {'request_field_name': '2021-01-01T00:00:00Z'}
