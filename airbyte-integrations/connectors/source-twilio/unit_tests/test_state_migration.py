# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import copy

import pytest
from components import TwilioStateMigration


@pytest.mark.parametrize("cursor_field", ["date_sent", "date_created", "end_time"])
def test_global_cursor_migration_preserves_checkpoint_metadata(cursor_field):
    state = {
        "use_global_cursor": True,
        "state": {cursor_field: "2022-11-16T00:00:00Z"},
        "states": [
            {
                "partition": {"subresource_uri": "/2010-04-01/Accounts/AC123/Messages.json", "parent_slice": {}},
                "cursor": {cursor_field: "2022-11-01T00:00:00Z"},
            }
        ],
        "lookback_window": 3600,
        "parent_state": {"accounts": {"state": {"date_created": "2022-11-10T00:00:00Z"}}},
    }
    original = copy.deepcopy(state)
    migration = TwilioStateMigration()

    assert migration.should_migrate(state)
    migrated = migration.migrate(state)

    assert migrated == {key: value for key, value in original.items() if key != "states"}
    assert state == original
    assert not migration.should_migrate(migrated)


@pytest.mark.parametrize(
    "mode,global_state",
    [
        (False, None),
        (False, {}),
        (False, {"date_sent": "2022-11-16T00:00:00Z"}),
        (None, None),
        (None, {}),
        (None, {"date_sent": "2022-11-16T00:00:00Z"}),
        (True, None),
        (True, {}),
    ],
)
def test_partition_checkpoints_preserved_without_authoritative_global_state(mode, global_state):
    state = {
        "states": [
            {
                "partition": {"subresource_uri": f"/2010-04-01/Accounts/{sid}/Messages.json"},
                "cursor": {"date_sent": date},
            }
            for sid, date in (("AC123", "2022-11-01T00:00:00Z"), ("AC456", "2022-11-15T00:00:00Z"))
        ],
    }
    if mode is not None:
        state["use_global_cursor"] = mode
    if global_state is not None:
        state["state"] = global_state
    expected = copy.deepcopy(state)
    for partition in expected["states"]:
        partition["partition"]["parent_slice"] = {}
    migration = TwilioStateMigration()

    assert migration.should_migrate(state)
    migrated = migration.migrate(state)

    assert migrated == expected
    assert not migration.should_migrate(migrated)
