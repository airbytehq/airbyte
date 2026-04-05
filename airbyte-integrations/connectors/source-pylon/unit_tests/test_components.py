# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from components import MigrateIssuesCursorFromCreatedAtToUpdatedAt


@pytest.fixture
def migration():
    return MigrateIssuesCursorFromCreatedAtToUpdatedAt()


class TestMigrateIssuesCursorFromCreatedAtToUpdatedAt:
    def test_should_migrate_when_created_at_present(self, migration):
        assert migration.should_migrate({"created_at": "2026-03-01T00:00:00Z"}) is True

    def test_should_not_migrate_when_updated_at_already_present(self, migration):
        assert migration.should_migrate({"updated_at": "2026-03-01T00:00:00Z"}) is False

    def test_should_not_migrate_when_both_present(self, migration):
        state = {"created_at": "2026-03-01T00:00:00Z", "updated_at": "2026-03-15T00:00:00Z"}
        assert migration.should_migrate(state) is False

    def test_should_not_migrate_empty_state(self, migration):
        assert migration.should_migrate({}) is False

    def test_migrate_renames_created_at_to_updated_at(self, migration):
        old_state = {"created_at": "2026-03-01T00:00:00Z"}
        new_state = migration.migrate(old_state)
        assert new_state == {"updated_at": "2026-03-01T00:00:00Z"}
        assert "created_at" not in new_state

    def test_migrate_preserves_cursor_value(self, migration):
        timestamp = "2024-01-15T12:30:45Z"
        new_state = migration.migrate({"created_at": timestamp})
        assert new_state["updated_at"] == timestamp
