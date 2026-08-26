#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock


def test_application_cursor_state_migration_drops_global_cursor(components_module):
    state = {"applied_at": "2024-01-01T00:00:00.000Z"}

    assert components_module.ApplicationCursorStateMigration().migrate(state) == {}


def test_application_cursor_state_migration_drops_partition_cursor(components_module):
    state = {
        "states": [
            {
                "partition": {"application_id": 42},
                "cursor": {"applied_at": "2024-01-01T00:00:00.000Z"},
            }
        ]
    }

    assert components_module.ApplicationCursorStateMigration().migrate(state) == {
        "states": [
            {
                "partition": {"application_id": 42},
                "cursor": {},
            }
        ]
    }


def test_application_cursor_state_migration_drops_child_parent_state(components_module):
    state = {
        "states": [
            {
                "partition": {"application_id": 42},
                "cursor": {"updated_at": "2024-01-02T00:00:00.000Z"},
            }
        ],
        "parent_state": {"applications": {"applied_at": "2024-01-01T00:00:00.000Z"}},
    }

    assert components_module.ApplicationCursorStateMigration().migrate(state) == {
        "states": [
            {
                "partition": {"application_id": 42},
                "cursor": {"updated_at": "2024-01-02T00:00:00.000Z"},
            }
        ],
        "parent_state": {"applications": {}},
    }


def test_application_cursor_state_migration_drops_nested_child_parent_state(
    components_module,
):
    state = {
        "states": [
            {
                "partition": {"application_id": 42},
                "parent_state": {"applications": {"applied_at": "2024-01-01T00:00:00.000Z"}},
                "cursor": {"updated_at": "2024-01-02T00:00:00.000Z"},
            }
        ]
    }

    assert components_module.ApplicationCursorStateMigration().migrate(state) == {
        "states": [
            {
                "partition": {"application_id": 42},
                "parent_state": {"applications": {}},
                "cursor": {"updated_at": "2024-01-02T00:00:00.000Z"},
            }
        ]
    }


def test_application_cursor_state_migration_is_noop_without_legacy_cursor(components_module):
    state = {"created_at": "2024-01-01T00:00:00.000Z"}

    assert components_module.ApplicationCursorStateMigration().migrate(state) is state


def test_application_cursor_state_migration_should_migrate_only_with_legacy_cursor(
    components_module,
):
    migration = components_module.ApplicationCursorStateMigration()

    assert migration.should_migrate({"applied_at": "2024-01-01T00:00:00.000Z"})
    assert not migration.should_migrate({"created_at": "2024-01-01T00:00:00.000Z"})


def test_per_partition_to_flat_state_migration_uses_minimum_cursor(components_module):
    declarative_stream = MagicMock()
    declarative_stream.incremental_sync.cursor_field = "updated_at"
    declarative_stream.parameters = {}
    migration = components_module.PerPartitionToFlatStateMigration(declarative_stream, {})

    state = {
        "states": [
            {"cursor": {"updated_at": "2024-01-03T00:00:00.000Z"}},
            {"cursor": {"updated_at": "2024-01-01T00:00:00.000Z"}},
        ],
        "state": {"updated_at": "2024-01-02T00:00:00.000Z"},
        "use_global_cursor": True,
        "lookback_window": "P1D",
        "parent_state": {"applications": {"updated_at": "2024-01-04T00:00:00.000Z"}},
        "42": {"updated_at": "2024-01-05T00:00:00.000Z"},
    }

    assert migration.migrate(state) == {"updated_at": "2024-01-01T00:00:00.000Z"}


def test_per_partition_to_flat_state_migration_returns_empty_without_cursor(components_module):
    declarative_stream = MagicMock()
    declarative_stream.incremental_sync.cursor_field = "updated_at"
    declarative_stream.parameters = {}
    migration = components_module.PerPartitionToFlatStateMigration(declarative_stream, {})

    assert migration.migrate({"states": [], "use_global_cursor": True}) == {}


def test_per_partition_to_flat_state_migration_should_migrate_flat_state_only(
    components_module,
):
    declarative_stream = MagicMock()
    declarative_stream.incremental_sync.cursor_field = "updated_at"
    declarative_stream.parameters = {}
    migration = components_module.PerPartitionToFlatStateMigration(declarative_stream, {})

    assert migration.should_migrate({"states": [{"cursor": {"updated_at": "2024-01-01T00:00:00.000Z"}}]})
    assert not migration.should_migrate({"updated_at": "2024-01-01T00:00:00.000Z"})
