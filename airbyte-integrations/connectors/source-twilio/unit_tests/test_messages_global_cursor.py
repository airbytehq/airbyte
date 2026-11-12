# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from urllib.parse import parse_qs, urlparse

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"


def partition(sid, cursor):
    return {
        "partition": {"subresource_uri": f"/2010-04-01/Accounts/{sid}/Messages.json", "parent_slice": {}},
        "cursor": {"date_sent": cursor},
    }


@pytest.mark.parametrize(
    "stream_state,expected_start",
    [
        pytest.param(
            {"states": [partition("AC123", "2025-10-10T00:00:00Z")], "state": {"date_sent": "2026-11-10T00:00:00Z"}, "lookback_window": 0},
            "2026-11-09 23:55:00Z",
            id="mixed",
        ),
        pytest.param(
            {"states": [partition("AC123", "2026-11-10T00:00:00Z"), partition("AC456", "2026-11-09T00:00:00Z")]},
            "2026-11-08 23:55:00Z",
            id="partition-only",
        ),
        pytest.param({}, "2026-11-08 00:00:00Z", id="new"),
        pytest.param(
            {"use_global_cursor": True, "state": {"date_sent": "2026-11-10T00:00:00Z"}, "parent_state": {}},
            "2026-11-09 23:55:00Z",
            id="global",
        ),
    ],
)
@freeze_time("2026-11-11 00:00:00+00:00")
def test_messages_read_uses_global_cursor(stream_state, expected_start):
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(url=f"{BASE}/Accounts.json", query_params={"PageSize": "1000"}),
            HttpResponse(
                body=json.dumps(
                    {"accounts": [{"sid": "AC123", "subresource_uris": {"messages": "/2010-04-01/Accounts/AC123/Messages.json"}}]}
                ),
                status_code=200,
            ),
        )
        http_mocker.get(
            HttpRequest(url=f"{BASE}/Accounts/AC123/Messages.json", query_params=ANY_QUERY_PARAMS),
            HttpResponse(body=json.dumps({"messages": [{"sid": "SM123", "date_sent": "2026-11-10T12:00:00Z"}]}), status_code=200),
        )
        config = {**TEST_CONFIG, "start_date": "2026-11-08T00:00:00Z", "lookback_window": 5}
        if "states" in stream_state:
            config["start_date"] = "2025-10-08T00:00:00Z"
        state = StateBuilder().with_stream_state("messages", stream_state).build()
        catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()
        output = read(get_source(config, state), config, catalog, state)
        requests = [request for request in http_mocker._mocker.request_history if "/Messages.json" in request.url]
        assert parse_qs(urlparse(requests[0].url).query)["DateSent>"] == [expected_start]
        assert output.errors == []
        assert len(output.records) >= 1
        emitted = output.state_messages[-1].state.stream.stream_state.__dict__
        assert emitted["use_global_cursor"] is True
        assert "states" not in emitted
        assert emitted["state"]["date_sent"] == "2026-11-10 12:00:00Z"
        assert "parent_state" in emitted


@pytest.fixture
def migration():
    from components import TwilioMessagesStateMigration

    return TwilioMessagesStateMigration()


@pytest.mark.parametrize("state", [{}, {"use_global_cursor": True, "state": {"date_sent": "2026-11-10T00:00:00Z"}}])
def test_messages_migration_leaves_global_and_new_state_alone(migration, state):
    assert not migration.should_migrate(state)


def test_messages_migration_preserves_parent_and_runtime_lookback(migration):
    state = {
        "states": [partition("AC123", "2026-11-01T00:00:00Z")],
        "state": {"date_sent": "2026-11-10T00:00:00Z"},
        "parent_state": {"accounts": {"cursor": "value"}},
        "lookback_window": 42,
    }
    migrated = migration.migrate(state)
    assert migrated == {key: value for key, value in state.items() if key != "states"} | {"use_global_cursor": True}
    assert "states" in state


@pytest.mark.parametrize("states", [[], [partition("AC123", None)]])
def test_messages_migration_missing_cursors_starts_fresh(migration, states):
    assert migration.migrate({"states": states}) == {"use_global_cursor": True, "state": {}}


def test_messages_migration_rejects_invalid_cursor(migration):
    with pytest.raises(ValueError):
        migration.migrate({"states": [partition("AC123", "invalid")]})
