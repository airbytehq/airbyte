# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs, urlparse

import components
import pytest
from conftest import TEST_CONFIG
from freezegun import freeze_time
from test_streams import BASE, read_from_stream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


def partition_state(account, cursor):
    return {
        "partition": {"subresource_uri": f"/2010-04-01/Accounts/{account}/Messages.json", "parent_slice": {}},
        "cursor": {"date_sent": cursor},
    }


@freeze_time("2022-11-16 12:03:11+00:00")
@pytest.mark.parametrize(
    "global_cursor,partition_cursors,expected",
    [
        ("2022-11-14T00:00:00Z", ["2022-01-01T00:00:00Z"], "2022-11-14 00:00:00Z"),
        (None, ["2022-11-15T00:00:00Z", "2022-11-14T01:00:00.000000+0000"], "2022-11-14 01:00:00Z"),
    ],
    ids=["mixed-global-authoritative", "partition-only-oldest"],
)
def test_messages_global_cursor(requests_mock, global_cursor, partition_cursors, expected):
    accounts = [f"AC{123 + i}" for i in range(len(partition_cursors))]
    payload = {"states": [partition_state(account, cursor) for account, cursor in zip(accounts, partition_cursors)]}
    if global_cursor:
        payload["state"] = {"date_sent": global_cursor}
    state = StateBuilder().with_stream_state("messages", payload).build()
    requests_mock.get(
        f"{BASE}/Accounts.json",
        json={
            "accounts": [
                {"sid": account, "subresource_uris": {"messages": f"/2010-04-01/Accounts/{account}/Messages.json"}} for account in accounts
            ]
        },
    )
    matchers = [requests_mock.get(f"{BASE}/Accounts/{account}/Messages.json", json={"messages": []}) for account in accounts]

    output = read_from_stream(TEST_CONFIG, "messages", SyncMode.incremental, state)

    lower_bounds = [parse_qs(urlparse(request.url).query)["DateSent>"][0] for matcher in matchers for request in matcher.request_history]
    assert all(matcher.called for matcher in matchers)
    assert min(lower_bounds) == expected
    assert all(lower >= expected for lower in lower_bounds)
    assert all(
        min(parse_qs(urlparse(request.url).query)["DateSent>"][0] for request in matcher.request_history) == expected
        for matcher in matchers
    )
    final_state = output.most_recent_state.stream_state.__dict__
    assert final_state["use_global_cursor"] is True
    assert final_state["state"] == {"date_sent": expected}
    assert "states" not in final_state


@pytest.mark.parametrize(
    "state", [{}, {"date_sent": "2022-11-14"}, {"states": []}, {"use_global_cursor": True, "state": {"date_sent": "2022-11-14"}}]
)
def test_messages_migration_leaves_non_partition_state(state):
    assert not components.TwilioMessagesStateMigration().should_migrate(state)


@pytest.mark.parametrize("cursor", ["2022-11-14T00:00:00Z", "2022-11-14", "2022-11-14T00:00:00.000000+0000", "2022-11-14 00:00:00Z"])
def test_messages_migration_cursor_formats_and_metadata(cursor):
    state = {
        "states": [partition_state("AC123", "2022-11-15T00:00:00Z"), partition_state("AC124", cursor)],
        "lookback_window": 17,
        "parent_state": {"accounts": {}},
    }
    migration = components.TwilioMessagesStateMigration()
    assert migration.should_migrate(state)
    assert migration.migrate(state) == {
        "use_global_cursor": True,
        "state": {"date_sent": cursor},
        "lookback_window": 17,
        "parent_state": {"accounts": {}},
    }


def test_messages_migration_rejects_invalid_cursor():
    with pytest.raises(ValueError, match="Unsupported messages date_sent cursor"):
        components.TwilioMessagesStateMigration().migrate({"states": [partition_state("AC123", "invalid")]})


def test_messages_migration_compares_timezones():
    later = "2022-11-13T23:00:00.000000-0200"
    earlier = "2022-11-14T00:00:00Z"
    state = {"states": [partition_state("AC123", later), partition_state("AC124", earlier)]}
    assert components.TwilioMessagesStateMigration().migrate(state)["state"]["date_sent"] == earlier


@freeze_time("2022-11-16 12:03:11+00:00")
def test_message_media_incremental_checkpoint(requests_mock):
    messages_uri = "/2010-04-01/Accounts/AC123/Messages.json"
    media_uri = "/2010-04-01/Accounts/AC123/Messages/SM1/Media.json"
    requests_mock.get(f"{BASE}/Accounts.json", json={"accounts": [{"sid": "AC123", "subresource_uris": {"messages": messages_uri}}]})
    requests_mock.get(
        f"https://api.twilio.com{messages_uri}",
        json={
            "messages": [{"sid": "SM1", "date_sent": "2022-11-16T01:00:00Z", "num_media": "1", "subresource_uris": {"media": media_uri}}]
        },
    )
    media = requests_mock.get(
        f"https://api.twilio.com{media_uri}",
        json={"media_list": [{"sid": "ME1", "date_created": "2022-11-16T01:05:00Z"}]},
    )
    config = {**TEST_CONFIG, "start_date": "2022-11-15T00:00:00Z"}
    first = read_from_stream(config, "message_media", SyncMode.incremental)
    checkpoint = first.most_recent_state.stream_state.__dict__
    assert len(first.records) == 1
    assert checkpoint["use_global_cursor"] is False
    assert checkpoint["states"] == [
        {
            "partition": {"subresource_uri": media_uri, "parent_slice": {"subresource_uri": messages_uri, "parent_slice": {}}},
            "cursor": {"date_created": "2022-11-16"},
        }
    ]
    assert checkpoint.get("parent_state", {}) == {}
    media.reset()
    state = StateBuilder().with_stream_state("message_media", checkpoint).build()
    read_from_stream(config, "message_media", SyncMode.incremental, state)
    assert media.called
    assert all(parse_qs(urlparse(request.url).query)["DateCreated>"] == ["2022-11-16"] for request in media.request_history)
