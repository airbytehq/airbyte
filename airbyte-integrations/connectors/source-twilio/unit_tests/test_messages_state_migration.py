# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from components import TwilioMessagesStateMigration


@pytest.mark.parametrize(
    "input_state,expected_state",
    [
        (
            {
                "states": [
                    {"cursor": {"date_sent": "2025-01-01T00:30:00+01:00"}},
                    {"cursor": {"date_sent": "2024-12-31T23:45:00Z"}},
                    {"cursor": {}},
                ],
                "parent_state": {},
                "lookback_window": 30,
            },
            {
                "use_global_cursor": True,
                "state": {"date_sent": "2025-01-01T00:30:00+01:00"},
                "lookback_window": 30,
                "parent_state": {},
            },
        ),
        (
            {"states": [{"cursor": {"date_sent": "2025-01-01T00:00:00Z"}}]},
            {"use_global_cursor": True, "state": {"date_sent": "2025-01-01T00:00:00Z"}, "lookback_window": 0},
        ),
        ({}, None),
        ({"use_global_cursor": False, "states": [{"cursor": {}}]}, None),
        ({"use_global_cursor": True, "state": {"date_sent": "2025-01-01T00:00:00Z"}}, None),
    ],
)
def test_messages_state_migration(input_state, expected_state):
    migration = TwilioMessagesStateMigration()
    assert migration.should_migrate(input_state) == (expected_state is not None)
    if expected_state is not None:
        migrated = migration.migrate(input_state)
        assert migrated == expected_state
        assert not migration.should_migrate(migrated)


def test_messages_state_migration_invalid_partition_cursor():
    with pytest.raises(ValueError):
        TwilioMessagesStateMigration().should_migrate({"states": [{"cursor": {"date_sent": "invalid"}}]})
