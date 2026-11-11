#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
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
