# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import copy
from urllib.parse import parse_qs, urlparse

import components
import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"
PARTITION = {"subresource_uri": "/2010-04-01/Accounts/AC123/Messages.json", "parent_slice": {}}
GLOBAL_CURSOR = {"date_sent": "2022-11-15T00:00:00Z"}


@freeze_time("2022-11-16 12:03:11+00:00")
@pytest.mark.parametrize(
    "use_global_cursor,partition_cursor,has_global_cursor,expected_start",
    [
        pytest.param(True, "2022-11-01T00:00:00Z", True, "2022-11-15 00:00:00Z", id="global_mode_stale_partition"),
        pytest.param(False, "2022-11-01T00:00:00Z", True, "2022-11-01 00:00:00Z", id="per_partition_mode_stale_partition"),
        pytest.param(False, "2022-11-15T12:00:00Z", True, "2022-11-15 12:00:00Z", id="per_partition_mode_newer_partition"),
        pytest.param(True, None, True, "2022-11-15 00:00:00Z", id="global_only"),
        pytest.param(False, None, False, "2022-11-01 00:00:00Z", id="empty"),
    ],
)
def test_messages_cursor_precedence(requests_mock, use_global_cursor, partition_cursor, has_global_cursor, expected_start):
    stream_state = {}
    if has_global_cursor:
        stream_state = {"state": GLOBAL_CURSOR, "lookback_window": 0, "use_global_cursor": use_global_cursor}
    if partition_cursor:
        stream_state["states"] = [{"partition": PARTITION, "cursor": {"date_sent": partition_cursor}}]
    state = StateBuilder().with_stream_state("messages", stream_state).build()
    config = {**TEST_CONFIG, "start_date": "2022-11-01T00:00:00Z"}
    catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()
    requests_mock.get(
        f"{BASE}/Accounts.json",
        json={"accounts": [{"sid": "AC123", "subresource_uris": {"messages": PARTITION["subresource_uri"]}}]},
    )
    messages = requests_mock.get(
        f"{BASE}/Accounts/AC123/Messages.json",
        json={"messages": [{"sid": "SM_NEW", "date_sent": "2022-11-15T13:00:00Z"}]},
    )

    output = read(get_source(config, state), config, catalog, state)

    assert not output.errors
    assert messages.call_count == 1
    query = parse_qs(urlparse(messages.last_request.url).query)
    assert query["DateSent>"] == [expected_start]
    assert query["DateSent<"] == ["2022-11-16 12:03:11Z"]
    assert len(output.records) == 1
    final_state = output.most_recent_state.stream_state.__dict__
    assert final_state["use_global_cursor"] is use_global_cursor
    assert final_state["state"] == {"date_sent": "2022-11-15 13:00:00Z"}
    if use_global_cursor:
        assert "states" not in final_state
    else:
        assert final_state["states"] == [{"partition": PARTITION, "cursor": {"date_sent": "2022-11-15 13:00:00Z"}}]


@pytest.mark.parametrize("cursor", ["2022-11-15T00:00:00Z", "2022-11-15 00:00:00Z", "2022-11-15", "2022-11-15T00:00:00.123+0000"])
def test_global_mode_migration_preserves_other_state(cursor):
    state = {
        "use_global_cursor": True,
        "state": {"date_sent": cursor},
        "states": [{"partition": PARTITION, "cursor": {"date_sent": "2022-11-01T00:00:00Z"}}],
        "lookback_window": 123,
        "parent_state": {"accounts": {"cursor": "value"}},
        "extra": "preserved",
    }
    original = copy.deepcopy(state)
    migration = components.TwilioMessagesGlobalStateMigration()

    assert migration.should_migrate(state)
    migrated = migration.migrate(state)
    assert migrated == {key: value for key, value in original.items() if key != "states"}
    assert state == original
    assert not migration.should_migrate(migrated)


@pytest.mark.parametrize(
    "state",
    [
        {},
        {"use_global_cursor": True, "state": GLOBAL_CURSOR},
        {"use_global_cursor": False, "state": GLOBAL_CURSOR, "states": []},
        {"state": GLOBAL_CURSOR, "states": []},
        {"use_global_cursor": True, "states": []},
        *[
            {"use_global_cursor": True, "state": value, "states": []}
            for value in (
                None,
                [],
                "invalid",
                {},
                {"date_sent": None},
                {"date_sent": 123},
                {"date_sent": "invalid"},
                {"date_sent": "2022-02-30"},
            )
        ],
    ],
)
def test_global_mode_migration_leaves_other_states_untouched(state):
    original = copy.deepcopy(state)
    assert not components.TwilioMessagesGlobalStateMigration().should_migrate(state)
    assert state == original
