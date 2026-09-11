# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


@dataclass
class MigrateIssuesCursorFromCreatedAtToUpdatedAt(StateMigration):
    """
    Migrates the issues stream state cursor from created_at to updated_at.

    Through v0.0.7, issues used GET /issues with created_at as the cursor.
    From v0.0.8 onward, issues uses POST /issues/search with updated_at as the cursor.

    A 1:1 rename of the cursor value is unsafe: created_at and updated_at describe
    disjoint event timelines, and any issue with created_at < state but updated_at < state
    would be permanently excluded from incremental syncs after the upgrade. Since prior
    versions never captured updates to existing issues, those updates are exactly what
    would be missed.

    Instead, this migration rewinds the cursor to the connection's configured start_date
    (or to 30 days ago if start_date is unset, matching the manifest default), forcing the
    next sync to re-pull all issues with their current updated_at values. This is effectively
    a one-time backfill of the issues stream on first sync after upgrade.
    """

    config: Mapping[str, Any]

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if not stream_state:
            return False
        return "created_at" in stream_state and "updated_at" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        rewound_cursor = self._resolve_rewind_cursor()
        return {"updated_at": rewound_cursor}

    def _resolve_rewind_cursor(self) -> str:
        start_date = self.config.get("start_date")
        if start_date:
            return start_date
        return (datetime.now(tz=timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
