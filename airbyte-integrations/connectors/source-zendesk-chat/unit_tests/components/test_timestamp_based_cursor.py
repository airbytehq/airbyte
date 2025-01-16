#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from source_zendesk_chat.components.timestamp_based_cursor import ZendeskChatTimestampCursor

from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType


def _get_cursor(config, cursor_field, use_microseconds) -> ZendeskChatTimestampCursor:
    cursor = ZendeskChatTimestampCursor(
        start_datetime="2020-10-01T00:00:00Z",
        cursor_field=cursor_field,
        datetime_format="%s",
        config=config,
        parameters={},
        use_microseconds=f"{{{ {use_microseconds} }}}",
    )
    # patching missing parts
    cursor.start_time_option = RequestOption(
        field_name=cursor_field,
        inject_into=RequestOptionType.request_parameter,
        parameters={},
    )
    return cursor


@pytest.mark.parametrize(
    "use_microseconds, input_slice, expected",
    [
        (True, {"start_time": 1}, {"start_time": 1000000}),
    ],
)
def test_timestamp_based_cursor_add_microseconds(config, use_microseconds, input_slice, expected) -> None:
    cursor = _get_cursor(config, "start_time", use_microseconds)
    test_result = cursor.add_microseconds({}, input_slice)
    assert test_result == expected


@pytest.mark.parametrize(
    "use_microseconds, input_slice, expected",
    [
        (True, {"start_time": 1}, {"start_time": 1000000}),
        (False, {"start_time": 1}, {"start_time": 1}),
    ],
    ids=[
        "WITH `use_microseconds`",
        "WITHOUT `use_microseconds`",
    ],
)
def test_timestamp_based_cursor_get_request_params(config, use_microseconds, input_slice, expected) -> None:
    cursor = _get_cursor(config, "start_time", use_microseconds)
    assert cursor.get_request_params(stream_slice=input_slice) == expected
