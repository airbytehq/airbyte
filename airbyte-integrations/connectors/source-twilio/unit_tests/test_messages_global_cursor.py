#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import copy

import components
import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"


@pytest.mark.parametrize("global_cursor", [True, False], ids=["mixed-state", "partition-only"])
@freeze_time("2024-01-05 00:00:00+00:00")
def test_messages_read_uses_global_cursor(requests_mock, global_cursor):
    accounts = ["AC123", "AC456"]
    requests_mock.get(
        f"{BASE}/Accounts.json",
        json={
            "accounts": [
                {
                    "sid": account,
                    "subresource_uris": {"messages": f"/2010-04-01/Accounts/{account}/Messages.json"},
                }
                for account in accounts
            ]
        },
    )
    for index, account in enumerate(accounts):
        requests_mock.get(
            f"{BASE}/Accounts/{account}/Messages.json",
            json={"messages": [{"sid": f"SM{index}", "date_sent": f"2024-01-04T0{index}:00:00Z"}]},
        )
    stream_state = {
        "states": [
            {
                "partition": {"subresource_uri": f"/2010-04-01/Accounts/{account}/Messages.json"},
                "cursor": {"date_sent": f"2024-01-0{index + 1}T00:00:00Z"},
            }
            for index, account in enumerate(accounts)
        ],
        "use_global_cursor": False,
    }
    if global_cursor:
        stream_state["state"] = {"date_sent": "2024-01-03T00:00:00Z"}
    state = StateBuilder().with_stream_state("messages", stream_state).build()
    config = {**TEST_CONFIG, "start_date": "2024-01-01T00:00:00Z"}
    catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()

    output = read(get_source(config, state), config, catalog, state)

    expected_start = "2024-01-03 00:00:00Z" if global_cursor else "2024-01-01 00:00:00Z"
    for account in accounts:
        requests = [request for request in requests_mock.request_history if f"/{account}/Messages.json" in request.url]
        assert len(requests) == 1, f"Expected one Messages request for {account}"
        assert requests[0].qs["datesent>"] == [expected_start.lower()]
    assert output.errors == []
    assert {record.record.data["sid"] for record in output.records} == {"SM0", "SM1"}
    final_state = vars(output.state_messages[-1].state.stream.stream_state)
    assert final_state["use_global_cursor"] is True
    assert final_state["state"]["date_sent"] == "2024-01-04 01:00:00Z"
    assert "states" not in final_state


@pytest.mark.parametrize(
    "state, should_migrate, expected",
    [
        ({}, False, {}),
        ({"date_sent": "2024-01-01T00:00:00Z"}, False, {"date_sent": "2024-01-01T00:00:00Z"}),
        ({"states": [{"cursor": {}}]}, True, {"states": [{"cursor": {}}]}),
        (
            {"states": [{"cursor": {"date_sent": "2024-01-02T00:00:00Z"}}, {"cursor": {"date_sent": "2024-01-01T00:00:00Z"}}]},
            True,
            {"use_global_cursor": True, "state": {"date_sent": "2024-01-01T00:00:00Z"}},
        ),
        (
            {"use_global_cursor": True, "state": {"date_sent": "2024-01-03T00:00:00Z"}},
            False,
            {"use_global_cursor": True, "state": {"date_sent": "2024-01-03T00:00:00Z"}},
        ),
        (
            {
                "states": [{"cursor": {"date_sent": "2024-01-01T00:00:00Z"}}],
                "state": {"date_sent": "2024-01-03T00:00:00Z"},
                "lookback_window": 60,
                "parent_state": {"accounts": {}},
            },
            True,
            {
                "use_global_cursor": True,
                "state": {"date_sent": "2024-01-03T00:00:00Z"},
                "lookback_window": 60,
                "parent_state": {"accounts": {}},
            },
        ),
    ],
)
def test_messages_state_migration(state, should_migrate, expected):
    original = copy.deepcopy(state)
    migration = components.TwilioMessagesStateMigration()
    assert migration.should_migrate(state) is should_migrate
    assert migration.migrate(state) == expected
    assert state == original
