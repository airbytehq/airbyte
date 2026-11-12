#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"
NOW = "2022-11-16 12:03:11+00:00"
NOW_CURSOR = "2022-11-16 12:03:11Z"
RECENT_CURSOR = "2022-11-13T12:11:10Z"
STALE_CURSOR = "2022-03-01T00:00:00Z"


def _account(sid: str) -> dict:
    return {
        "sid": sid,
        "date_created": "2022-01-01T00:00:00Z",
        "subresource_uris": {"messages": f"/2010-04-01/Accounts/{sid}/Messages.json"},
    }


def _partition(sid: str) -> dict:
    return {"subresource_uri": f"/2010-04-01/Accounts/{sid}/Messages.json", "parent_slice": {}}


def _read_messages(requests_mock, account_sids, stream_state):
    requests_mock.get(f"{BASE}/Accounts.json", json={"accounts": [_account(sid) for sid in account_sids]})
    messages_matchers = {
        sid: requests_mock.get(
            f"{BASE}/Accounts/{sid}/Messages.json",
            json={"messages": [{"sid": f"SM_{sid}", "account_sid": sid, "date_sent": "2022-11-15T10:00:00Z"}]},
        )
        for sid in account_sids
    }
    state = StateBuilder().with_stream_state("messages", stream_state).build()
    config = {**TEST_CONFIG, "start_date": "2000-01-01T00:00:00Z"}
    catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()
    output = read(get_source(config, state), config, catalog, state)
    lower_bounds = {
        sid: [parse_qs(urlparse(request.url).query)["DateSent>"][0] for request in matcher.request_history]
        for sid, matcher in messages_matchers.items()
    }
    return output, lower_bounds


@freeze_time(NOW)
@pytest.mark.parametrize(
    "account_sids,stream_state,expected_lower_bounds",
    [
        pytest.param(
            ["AC123"],
            {
                "use_global_cursor": False,
                "states": [{"partition": _partition("AC123"), "cursor": {"date_sent": STALE_CURSOR}}],
                "state": {"date_sent": RECENT_CURSOR},
                "lookback_window": 0,
            },
            {"AC123": ["2022-11-13 12:11:10Z"]},
            id="stale_partition_cursor_with_recent_global_cursor",
        ),
        pytest.param(
            ["AC123", "AC456"],
            {
                "states": [
                    {"partition": _partition("AC123"), "cursor": {"date_sent": STALE_CURSOR}},
                    {"partition": _partition("AC456"), "cursor": {"date_sent": "2022-11-01T00:00:00Z"}},
                ],
                "state": {"date_sent": RECENT_CURSOR},
            },
            {"AC123": ["2022-11-13 12:11:10Z"], "AC456": ["2022-11-13 12:11:10Z"]},
            id="multiple_accounts_resume_from_global_cursor",
        ),
        pytest.param(
            ["AC123", "AC456"],
            {
                "states": [
                    {"partition": _partition("AC123"), "cursor": {"date_sent": "2022-11-14T00:00:00Z"}},
                    {"partition": _partition("AC456"), "cursor": {"date_sent": RECENT_CURSOR}},
                ],
            },
            {"AC123": ["2022-11-13 12:11:10Z"], "AC456": ["2022-11-13 12:11:10Z"]},
            id="partition_only_state_resumes_from_oldest_partition_cursor",
        ),
    ],
)
def test_messages_incremental_read_resumes_from_global_cursor(requests_mock, account_sids, stream_state, expected_lower_bounds):
    output, lower_bounds = _read_messages(requests_mock, account_sids, stream_state)

    assert lower_bounds == expected_lower_bounds
    assert sorted(record.record.data["sid"] for record in output.records) == sorted(f"SM_{sid}" for sid in account_sids)
    final_state = output.most_recent_state.stream_state.__dict__
    assert final_state["use_global_cursor"] is True
    assert "states" not in final_state
    assert final_state["state"] == {"date_sent": "2022-11-15 10:00:00Z"}


@freeze_time(NOW)
def test_messages_second_incremental_read_uses_emitted_state(requests_mock):
    first_output, _ = _read_messages(
        requests_mock,
        ["AC123"],
        {
            "states": [{"partition": _partition("AC123"), "cursor": {"date_sent": STALE_CURSOR}}],
            "state": {"date_sent": RECENT_CURSOR},
        },
    )
    emitted_state = first_output.most_recent_state.stream_state.__dict__

    requests_mock.reset_mock()
    _, lower_bounds = _read_messages(requests_mock, ["AC123"], emitted_state)

    assert lower_bounds == {"AC123": ["2022-11-15 10:00:00Z"]}
