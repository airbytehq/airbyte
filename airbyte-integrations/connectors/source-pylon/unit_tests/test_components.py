# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import re

import pytest


ISO_8601_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class TestMigrateIssuesCursorFromCreatedAtToUpdatedAt:
    def test_should_migrate_when_created_at_present(self, components_module):
        migration = components_module.MigrateIssuesCursorFromCreatedAtToUpdatedAt(config={"start_date": "2024-01-01T00:00:00Z"})
        assert migration.should_migrate({"created_at": "2026-03-01T00:00:00Z"}) is True

    def test_should_not_migrate_when_updated_at_already_present(self, components_module):
        migration = components_module.MigrateIssuesCursorFromCreatedAtToUpdatedAt(config={"start_date": "2024-01-01T00:00:00Z"})
        assert migration.should_migrate({"updated_at": "2026-03-01T00:00:00Z"}) is False

    def test_should_not_migrate_when_both_present(self, components_module):
        migration = components_module.MigrateIssuesCursorFromCreatedAtToUpdatedAt(config={"start_date": "2024-01-01T00:00:00Z"})
        state = {"created_at": "2026-03-01T00:00:00Z", "updated_at": "2026-03-15T00:00:00Z"}
        assert migration.should_migrate(state) is False

    def test_should_not_migrate_empty_state(self, components_module):
        migration = components_module.MigrateIssuesCursorFromCreatedAtToUpdatedAt(config={"start_date": "2024-01-01T00:00:00Z"})
        assert migration.should_migrate({}) is False

    def test_should_not_migrate_none_state(self, components_module):
        migration = components_module.MigrateIssuesCursorFromCreatedAtToUpdatedAt(config={"start_date": "2024-01-01T00:00:00Z"})
        assert migration.should_migrate(None) is False

    def test_migrate_rewinds_to_configured_start_date(self, components_module):
        migration = components_module.MigrateIssuesCursorFromCreatedAtToUpdatedAt(config={"start_date": "2024-01-01T00:00:00Z"})
        old_state = {"created_at": "2026-03-01T00:00:00Z"}
        new_state = migration.migrate(old_state)
        assert new_state == {"updated_at": "2024-01-01T00:00:00Z"}
        assert "created_at" not in new_state

    def test_migrate_ignores_old_cursor_value(self, components_module):
        # The whole point of the rewind: old cursor value is unsafe to reuse.
        migration = components_module.MigrateIssuesCursorFromCreatedAtToUpdatedAt(config={"start_date": "2024-06-01T00:00:00Z"})
        new_state = migration.migrate({"created_at": "2026-04-15T12:30:45Z"})
        assert new_state["updated_at"] == "2024-06-01T00:00:00Z"

    def test_migrate_falls_back_to_30_days_ago_when_start_date_missing(self, components_module):
        migration = components_module.MigrateIssuesCursorFromCreatedAtToUpdatedAt(config={})
        new_state = migration.migrate({"created_at": "2026-04-01T00:00:00Z"})
        assert ISO_8601_REGEX.match(new_state["updated_at"]) is not None

    def test_migrate_falls_back_when_start_date_empty_string(self, components_module):
        migration = components_module.MigrateIssuesCursorFromCreatedAtToUpdatedAt(config={"start_date": ""})
        new_state = migration.migrate({"created_at": "2026-04-01T00:00:00Z"})
        assert ISO_8601_REGEX.match(new_state["updated_at"]) is not None
