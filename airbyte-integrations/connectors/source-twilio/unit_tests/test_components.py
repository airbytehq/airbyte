# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from copy import deepcopy

import pytest
from components import TwilioStateMigration


@pytest.mark.parametrize("use_global_cursor", [False, True])
@pytest.mark.parametrize("global_state", [{}, {"date_sent": "2022-11-15T12:00:00Z"}])
def test_state_migration_preserves_authoritative_progress(use_global_cursor, global_state):
    state = {
        "use_global_cursor": use_global_cursor,
        "state": global_state,
        "lookback_window": 900,
        "parent_state": {"accounts": {"date_created": "2022-11-14T00:00:00Z"}},
        "states": [
            {
                "partition": {"subresource_uri": f"/2010-04-01/Accounts/{account}/Messages.json", "parent_slice": {}},
                "cursor": {"date_sent": cursor},
            }
            for account, cursor in [("AC123", "2022-11-13T12:00:00Z"), ("AC456", "2022-11-14T12:00:00Z")]
        ],
    }
    original_state = deepcopy(state)
    expected_state = deepcopy(state)
    if use_global_cursor and global_state:
        del expected_state["states"]

    migration = TwilioStateMigration()
    assert migration.should_migrate(state) == bool(use_global_cursor and global_state)
    migrated_state = migration.migrate(state)
    assert migrated_state == expected_state
    assert migration.migrate(migrated_state) == migrated_state
    assert not migration.should_migrate(migrated_state)
    assert state == original_state
