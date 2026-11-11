#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy

import pytest
from components import TwilioStalePartitionStateMigration


@pytest.mark.parametrize(
    "global_cursor,partition_cursor,stale",
    [
        ("2022-11-14 00:00:00Z", "2022-01-20 00:00:00Z", True),
        ("2022-11-14T00:00:00Z", "2022-01-20", True),
        ("2022-11-14", "2022-01-20T00:00:00Z", True),
        ("2022-11-14", "2022-11-14T00:00:00Z", False),
        ("2022-11-14", "2022-11-15 00:00:00Z", False),
        ("invalid", "2022-01-20", False),
        ("2022-11-14", "invalid", False),
        (None, "2022-01-20", False),
        ("2022-11-14", None, False),
    ],
)
def test_stale_partition_state_migration(global_cursor, partition_cursor, stale):
    entry = {"partition": {"subresource_uri": "/Messages.json", "parent_slice": {}}, "cursor": {"date_sent": partition_cursor}}
    state = {
        "states": [entry],
        "state": {"date_sent": global_cursor},
        "lookback_window": 17,
        "parent_state": {"accounts": {}},
        "use_global_cursor": False,
    }
    original = deepcopy(state)
    migration = TwilioStalePartitionStateMigration()

    assert migration.should_migrate(state) is stale
    assert migration.migrate(state) == {**original, "states": [] if stale else [entry]}
    assert state == original


@pytest.mark.parametrize(
    "state",
    [
        {},
        {"state": {"date_sent": "2022-11-14"}},
        {"states": []},
        {"states": [{"cursor": {"date_sent": "2022-01-20"}}]},
        {"state": {"date_sent": "2022-11-14"}, "states": [{"cursor": {}}]},
        {"state": {"date_sent": "2022-11-14"}, "states": [{"cursor": {"date_created": "2022-01-20"}}]},
    ],
)
def test_stale_partition_state_migration_no_op(state):
    assert not TwilioStalePartitionStateMigration().should_migrate(state)


def test_stale_partition_state_migration_preserves_other_partitions():
    entries = [
        {"partition": {"sid": sid}, "cursor": {"date_created": value}}
        for sid, value in [("old", "2022-01-20"), ("equal", "2022-11-14"), ("new", "2022-11-15"), ("invalid", "invalid")]
    ]
    state = {"state": {"date_created": "2022-11-14"}, "states": entries}
    migration = TwilioStalePartitionStateMigration()

    assert migration.should_migrate(state)
    migrated = migration.migrate(state)
    assert migrated == {**state, "states": entries[1:]}
    assert not migration.should_migrate(migrated)
