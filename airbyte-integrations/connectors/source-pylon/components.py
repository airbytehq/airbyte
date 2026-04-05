# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


class MigrateIssuesCursorFromCreatedAtToUpdatedAt(StateMigration):
    """
    Migrates the issues stream state cursor field from created_at to updated_at.

    In v0.0.5 and earlier, the issues stream used GET /issues with created_at as the
    cursor. In v0.0.6+, the stream uses POST /issues/search with updated_at as the cursor.
    This migration renames the state key so existing connections don't lose their cursor
    position and trigger a full re-sync.
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return "created_at" in stream_state and "updated_at" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"updated_at": stream_state["created_at"]}
