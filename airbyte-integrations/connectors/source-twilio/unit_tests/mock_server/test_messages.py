#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"
ACCOUNT_SIDS = ["AC123", "AC456"]
NOW = "2022-11-16 12:03:11Z"

MESSAGES = {
    "AC123": [{"sid": "SM_old_123", "date_sent": "2022-06-01T00:00:00Z"}, {"sid": "SM_new", "date_sent": "2022-11-15T10:00:00Z"}],
    "AC456": [{"sid": "SM_old_456", "date_sent": "2022-06-01T00:00:00Z"}],
}


def _messages_uri(account_sid):
    return f"/2010-04-01/Accounts/{account_sid}/Messages.json"


def _parse(value):
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)


def _register_mocks(requests_mock):
    requests_mock.get(
        f"{BASE}/Accounts.json",
        json={"accounts": [{"sid": sid, "subresource_uris": {"messages": _messages_uri(sid)}} for sid in ACCOUNT_SIDS]},
    )
    windows = {sid: [] for sid in ACCOUNT_SIDS}

    def _callback(account_sid):
        def _respond(request, context):
            query = parse_qs(urlparse(request.url).query)
            lower, upper = query["DateSent>"][0], query["DateSent<"][0]
            windows[account_sid].append((lower, upper))
            return {
                "messages": [
                    message
                    for message in MESSAGES[account_sid]
                    if _parse(lower) <= datetime.fromisoformat(message["date_sent"].replace("Z", "+00:00")) <= _parse(upper)
                ]
            }

        return _respond

    for sid in ACCOUNT_SIDS:
        requests_mock.get(f"https://api.twilio.com{_messages_uri(sid)}", json=_callback(sid))
    return windows


def _read(state):
    catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()
    config = {**TEST_CONFIG, "start_date": "2022-01-01T00:00:00Z"}
    return read(get_source(config, state), config, catalog, state)


@freeze_time("2022-11-16 12:03:11+00:00")
@pytest.mark.parametrize(
    "input_state,expected_lower_bound",
    [
        pytest.param(
            {
                "use_global_cursor": False,
                "state": {"date_sent": "2022-11-10T00:00:00Z"},
                "lookback_window": 0,
                "states": [
                    {
                        "partition": {"subresource_uri": _messages_uri("AC123"), "parent_slice": {}},
                        "cursor": {"date_sent": "2022-11-10T00:00:00Z"},
                    },
                    {
                        "partition": {"subresource_uri": _messages_uri("AC456"), "parent_slice": {}},
                        "cursor": {"date_sent": "2022-01-01T00:00:00Z"},
                    },
                ],
            },
            "2022-11-10 00:00:00Z",
            id="stale_partition_cursor_with_global_cursor",
        ),
        pytest.param(
            {
                "states": [
                    {"partition": {"subresource_uri": _messages_uri("AC123")}, "cursor": {"date_sent": "2022-11-12T00:00:00Z"}},
                    {"partition": {"subresource_uri": _messages_uri("AC456")}, "cursor": {"date_sent": "2022-11-10T00:00:00Z"}},
                ],
            },
            "2022-11-10 00:00:00Z",
            id="legacy_partition_cursors_without_global_cursor",
        ),
    ],
)
def test_messages_incremental_reads_every_account_from_the_global_cursor(input_state, expected_lower_bound, requests_mock):
    windows = _register_mocks(requests_mock)

    first_output = _read(StateBuilder().with_stream_state("messages", input_state).build())

    assert [record.record.data["sid"] for record in first_output.records] == ["SM_new"]
    assert windows == {sid: [(expected_lower_bound, NOW)] for sid in ACCOUNT_SIDS}
    emitted_state = first_output.most_recent_state.stream_state.__dict__
    assert emitted_state["use_global_cursor"] is True
    assert "states" not in emitted_state
    assert emitted_state["state"] == {"date_sent": "2022-11-15 10:00:00Z"}

    for sid in ACCOUNT_SIDS:
        windows[sid].clear()
    second_output = _read(StateBuilder().with_stream_state("messages", emitted_state).build())

    assert [record.record.data["sid"] for record in second_output.records] == ["SM_new"]
    assert windows == {sid: [("2022-11-15 10:00:00Z", NOW)] for sid in ACCOUNT_SIDS}
