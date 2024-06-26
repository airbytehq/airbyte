#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from source_zendesk_chat.components.id_incremental_cursor import ZendeskChatIdIncrementalCursor


def _get_cursor(config) -> ZendeskChatIdIncrementalCursor:
    return ZendeskChatIdIncrementalCursor(
        config = config,
        cursor_field = "id",
        field_name = "since_id",
        parameters = {},
    )


@pytest.mark.parametrize(
    "stream_state, expected_cursor_value, expected_state_value",
    [
        ({"id": 10}, 10, {'id': 10}),
    ],
    ids=[
        "SET Initial State and GET State"
    ]
)
def test_id_incremental_cursor_set_initial_state_and_get_stream_state(
    config, 
    stream_state,
    expected_cursor_value, 
    expected_state_value,
) -> None:
    cursor = _get_cursor(config)
    cursor.set_initial_state(stream_state)
    assert cursor._cursor == expected_cursor_value
    assert cursor._state == expected_cursor_value
    assert cursor.get_stream_state() == expected_state_value


@pytest.mark.parametrize(
    "test_record, expected",
    [
        ({"id": 123}, 123),
        ({"id": 456}, 456),
    ],
    ids=[
        "first",
        "second"
    ]
)
def test_id_incremental_cursor_close_slice(config, test_record, expected) -> None:
    cursor = _get_cursor(config)
    cursor.observe(stream_slice={}, record=test_record)
    cursor.close_slice(stream_slice={})
    assert cursor._cursor == expected
    

@pytest.mark.parametrize(
    "stream_state, input_slice, expected",
    [
        ({}, {"id": 1}, {}),
        ({"id": 2}, {"id": 1}, {"since_id": 2}),
    ],
    ids=[
        "No State",
        "With State"
    ]
)
def test_id_incremental_cursor_get_request_params(config, stream_state, input_slice, expected) -> None:
    cursor = _get_cursor(config)
    if stream_state:
        cursor.set_initial_state(stream_state)
    assert cursor.get_request_params(stream_slice=input_slice) == expected
    

@pytest.mark.parametrize(
    "stream_state, record, expected",
    [
        ({}, {"id": 1}, True),
        ({"id": 2}, {"id": 1}, False),
        ({"id": 2}, {"id": 3}, True),
    ],
    ids=[
        "No State",
        "With State > Record value",
        "With State < Record value",
    ]
)
def test_id_incremental_cursor_should_be_synced(config, stream_state, record, expected) -> None:
    cursor = _get_cursor(config)
    if stream_state:
        cursor.set_initial_state(stream_state)
    assert cursor.should_be_synced(record=record) == expected


@pytest.mark.parametrize(
    "first_record, second_record, expected",
    [
        ({"id": 2}, {"id": 1}, True),
        ({"id": 2}, {"id": 3}, False),
        ({"id": 3}, {}, True),
        ({}, {}, False),
    ],
    ids=[
        "First > Second - should synced",
        "First < Second - should not be synced",
        "Has First but no Second - should be synced",
        "Has no First and has no Second - should not be synced",
    ]
)
def test_id_incremental_cursor_is_greater_than_or_equal(config, first_record, second_record, expected) -> None:
    cursor = _get_cursor(config)
    assert cursor.is_greater_than_or_equal(first=first_record, second=second_record) == expected
