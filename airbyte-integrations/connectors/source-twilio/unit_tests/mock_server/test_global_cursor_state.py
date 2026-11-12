# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"
ACCOUNT_URI = "/2010-04-01/Accounts/AC123"
CONFIG = {**TEST_CONFIG, "start_date": "2022-06-15T00:00:00Z"}

ACCOUNTS_JSON = {
    "accounts": [
        {
            "sid": "AC123",
            "date_created": "2022-01-01T00:00:00Z",
            "subresource_uris": {
                name: f"{ACCOUNT_URI}/{name.capitalize()}.json" for name in ("calls", "conferences", "messages", "recordings")
            },
        }
    ],
}
MESSAGE_WITH_MEDIA = {
    "sid": "SM1",
    "num_media": "1",
    "date_sent": "2022-11-15T10:00:00Z",
    "subresource_uris": {"media": f"{ACCOUNT_URI}/Messages/SM1/Media.json"},
}


def _subresource_partition(name, **extra):
    return {**extra, "subresource_uri": f"{ACCOUNT_URI}/{name}.json", "parent_slice": {}}


# stream, child path, lower bound param, cursor field, stale partitions, stale cursor, global cursor,
# expected lower bound of every child request, expected child request count, child response
STREAMS = [
    pytest.param(
        "messages",
        "/Accounts/AC123/Messages.json",
        "DateSent>",
        "date_sent",
        [_subresource_partition("Messages")],
        "2022-07-01 00:00:00Z",
        "2022-11-15 10:00:00Z",
        "2022-11-15 10:00:00Z",
        1,
        {"messages": [{"sid": "SM1", "date_sent": "2022-11-15T10:00:00Z"}]},
        id="messages",
    ),
    pytest.param(
        "recordings",
        "/Accounts/AC123/Recordings.json",
        "DateCreated>",
        "date_created",
        [_subresource_partition("Recordings")],
        "2022-07-01 00:00:00Z",
        "2022-11-15 10:00:00Z",
        "2022-11-15 10:00:00Z",
        1,
        {"recordings": [{"sid": "RE1", "date_created": "2022-11-15T10:00:00Z"}]},
        id="recordings",
    ),
    pytest.param(
        "calls",
        "/Accounts/AC123/Calls.json",
        "EndTime>",
        "end_time",
        [_subresource_partition("Calls")],
        "2022-07-01",
        "2022-11-15",
        "2022-11-15",
        1,
        {"calls": [{"sid": "CA1", "end_time": "2022-11-15T10:00:00Z"}]},
        id="calls",
    ),
    pytest.param(
        "conferences",
        "/Accounts/AC123/Conferences.json",
        "DateCreated>",
        "date_created",
        [_subresource_partition("Conferences", conference_status=status) for status in ("init", "in-progress", "completed")],
        "2022-07-01",
        "2022-11-15",
        "2022-11-15",
        3,
        {"conferences": [{"sid": "CF1", "date_created": "2022-11-15T10:00:00Z"}]},
        id="conferences",
    ),
    pytest.param(
        "usage_records",
        "/Accounts/AC123/Usage/Records/Daily.json",
        "StartDate",
        "start_date",
        [{"account_sid": "AC123", "parent_slice": {}}],
        "2022-07-01",
        "2022-11-15",
        "2022-11-15",
        1,
        {"usage_records": [{"account_sid": "AC123", "category": "sms", "start_date": "2022-11-15", "end_date": "2022-11-15"}]},
        id="usage_records",
    ),
    pytest.param(
        "message_media",
        "/Accounts/AC123/Messages/SM1/Media.json",
        "DateCreated>",
        "date_created",
        [
            {
                "subresource_uri": f"{ACCOUNT_URI}/Messages/SM1/Media.json",
                "parent_slice": _subresource_partition("Messages"),
            }
        ],
        "2022-07-01",
        "2022-11-15",
        "2022-11-15",
        1,
        {"media_list": [{"sid": "ME1", "date_created": "2022-11-15T10:00:00Z"}]},
        id="message_media",
    ),
]


def _read(requests_mock, stream_name, child_path, child_response, stream_state):
    requests_mock.get(f"{BASE}/Accounts.json", json=ACCOUNTS_JSON)
    if stream_name == "message_media":
        # The parent `messages` stream is read in monthly windows; only the latest one holds the message with media.
        requests_mock.get(f"{BASE}/Accounts/AC123/Messages.json", json={"messages": []})
        requests_mock.get(
            f"{BASE}/Accounts/AC123/Messages.json",
            json={"messages": [MESSAGE_WITH_MEDIA]},
            additional_matcher=lambda request: parse_qs(urlparse(request.url).query)["DateSent<"] == ["2022-11-16 12:03:11Z"],
        )
    child_matcher = requests_mock.get(f"{BASE}{child_path}", json=child_response)

    state = StateBuilder().with_stream_state(stream_name, stream_state).build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    output = read(get_source(CONFIG, state), CONFIG, catalog, state)
    return output, child_matcher


def _lower_bounds(matcher, lower_key):
    return sorted(parse_qs(urlparse(request.url).query)[lower_key][0] for request in matcher.request_history)


@freeze_time("2022-11-16 12:03:11+00:00")
@pytest.mark.parametrize(
    "stream_name,child_path,lower_key,cursor_field,partitions,stale_cursor,global_cursor,expected_lower,expected_requests,child_response",
    STREAMS,
)
def test_global_cursor_state_ignores_leftover_partition_states(
    stream_name,
    child_path,
    lower_key,
    cursor_field,
    partitions,
    stale_cursor,
    global_cursor,
    expected_lower,
    expected_requests,
    child_response,
    requests_mock,
):
    """A state in global-cursor mode resumes from the global cursor even when stale per-partition states are still present."""
    stream_state = {
        "use_global_cursor": True,
        "state": {cursor_field: global_cursor},
        "states": [{"partition": partition, "cursor": {cursor_field: stale_cursor}} for partition in partitions],
        "lookback_window": 0,
    }

    output, child_matcher = _read(requests_mock, stream_name, child_path, child_response, stream_state)

    assert not output.errors
    # One request per partition, each starting at the global cursor: nothing before it is requested again.
    assert _lower_bounds(child_matcher, lower_key) == [expected_lower] * expected_requests
    assert len(output.records) == expected_requests

    final_state = output.most_recent_state.stream_state.__dict__
    assert final_state["use_global_cursor"] is True
    assert final_state["state"] == {cursor_field: global_cursor}
    assert "states" not in final_state


@freeze_time("2022-11-16 12:03:11+00:00")
def test_per_partition_state_still_resumes_from_partition_cursor(requests_mock):
    """Without `use_global_cursor`, a partition older than the global cursor is still read from its own cursor."""
    stream_state = {
        "use_global_cursor": False,
        "state": {"date_sent": "2022-11-15 10:00:00Z"},
        "states": [{"partition": _subresource_partition("Messages"), "cursor": {"date_sent": "2022-10-20 00:00:00Z"}}],
        "lookback_window": 0,
    }

    output, child_matcher = _read(
        requests_mock,
        "messages",
        "/Accounts/AC123/Messages.json",
        {"messages": [{"sid": "SM1", "date_sent": "2022-11-15T10:00:00Z"}]},
        stream_state,
    )

    assert not output.errors
    assert _lower_bounds(child_matcher, "DateSent>") == ["2022-10-20 00:00:00Z"]
    final_state = output.most_recent_state.stream_state.__dict__
    assert [partition_state["cursor"] for partition_state in final_state["states"]] == [{"date_sent": "2022-11-15 10:00:00Z"}]
