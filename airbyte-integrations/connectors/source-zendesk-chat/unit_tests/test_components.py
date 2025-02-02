
import pytest
import requests
from typing import Any, List, Mapping
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType



@pytest.fixture
def config() -> Mapping[str, Any]:
    return {
        "start_date": "2020-10-01T00:00:00Z",
        "subdomain": "",
        "credentials": {"credentials": "access_token", "access_token": "__access_token__"},
    }

@pytest.fixture
def bans_stream_record() -> Mapping[str, Any]:
    return {
        "ip_address": [{"reason": "test", "type": "ip_address", "id": 1234, "created_at": "2021-04-21T14:42:46Z", "ip_address": "0.0.0.0"}],
        "visitor": [
            {
                "type": "visitor",
                "id": 4444,
                "visitor_name": "Visitor 4444",
                "visitor_id": "visitor_id",
                "reason": "test",
                "created_at": "2021-04-27T13:25:01Z",
            }
        ],
    }

@pytest.fixture
def bans_stream_record_extractor_expected_output() -> List[Mapping[str, Any]]:
    return [
        {"reason": "test", "type": "ip_address", "id": 1234, "created_at": "2021-04-21T14:42:46Z", "ip_address": "0.0.0.0"},
        {
            "type": "visitor",
            "id": 4444,
            "visitor_name": "Visitor 4444",
            "visitor_id": "visitor_id",
            "reason": "test",
            "created_at": "2021-04-27T13:25:01Z",
        },
    ]

def _get_cursor(components_module, config):
    ZendeskChatIdIncrementalCursor = components_module.ZendeskChatIdIncrementalCursor
    return ZendeskChatIdIncrementalCursor(
        config=config,
        cursor_field="id",
        field_name="since_id",
        parameters={},
    )

@pytest.mark.parametrize(
    "stream_state, expected_cursor_value, expected_state_value",
    [
        ({"id": 10}, 10, {"id": 10}),
    ],
    ids=["SET Initial State and GET State"],
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
    ids=["first", "second"],
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
    ids=["No State", "With State"],
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
    ],
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
    ],
)
def test_id_incremental_cursor_is_greater_than_or_equal(config, first_record, second_record, expected) -> None:
    cursor = _get_cursor(config)
    assert cursor.is_greater_than_or_equal(first=first_record, second=second_record) == expected

def test_bans_stream_record_extractor(
    components_module,
    config,
    requests_mock,
    bans_stream_record,
    bans_stream_record_extractor_expected_output,
) -> None:
    ZendeskChatBansRecordExtractor = components_module.ZendeskChatBansRecordExtractor
    test_url = f"https://{config['subdomain']}.zendesk.com/api/v2/chat/bans"
    requests_mock.get(test_url, json=bans_stream_record)
    test_response = requests.get(test_url)
    assert ZendeskChatBansRecordExtractor().extract_records(test_response) == bans_stream_record_extractor_expected_output

def _get_paginator(components_module, config, id_field):
    ZendeskChatIdOffsetIncrementPaginationStrategy = components_module.ZendeskChatIdOffsetIncrementPaginationStrategy
    return ZendeskChatIdOffsetIncrementPaginationStrategy(
        config=config,
        page_size=1,
        id_field=id_field,
        parameters={},
    )

@pytest.mark.parametrize(
    "id_field, last_records, expected",
    [("id", [{"id": 1}], 2), ("id", [], None)],
)
def test_id_offset_increment_pagination_next_page_token(requests_mock, config, id_field, last_records, expected) -> None:
    paginator = _get_paginator(config, id_field)
    test_url = f"https://{config['subdomain']}.zendesk.com/api/v2/chat/agents"
    requests_mock.get(test_url, json=last_records)
    test_response = requests.get(test_url)
    assert paginator.next_page_token(test_response, last_records) == expected


def _get_paginator(components_module, config, time_field_name):
    ZendeskChatTimeOffsetIncrementPaginationStrategy = components_module.ZendeskChatTimeOffsetIncrementPaginationStrategy
    return ZendeskChatTimeOffsetIncrementPaginationStrategy(
        config=config,
        page_size=1,
        time_field_name=time_field_name,
        parameters={},
    )


@pytest.mark.parametrize(
    "time_field_name, response, last_records, expected",
    [
        ("end_time", {"chats": [{"update_timestamp": 1}], "end_time": 2}, [{"update_timestamp": 1}], 2),
        ("end_time", {"chats": [], "end_time": 3}, [], None),
    ],
)
def test_time_offset_increment_pagination_next_page_token(requests_mock, config, time_field_name, response, last_records, expected) -> None:
    paginator = _get_paginator(config, time_field_name)
    test_url = f"https://{config['subdomain']}.zendesk.com/api/v2/chat/chats"
    requests_mock.get(test_url, json=response)
    test_response = requests.get(test_url)
    assert paginator.next_page_token(test_response, last_records) == expected


def _get_cursor(components_module, config, cursor_field, use_microseconds):
    ZendeskChatTimestampCursor = components_module.ZendeskChatTimestampCursor
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
