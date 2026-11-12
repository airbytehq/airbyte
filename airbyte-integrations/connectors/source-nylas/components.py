# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


class EventsFlatPartitionStateMigration(StateMigration):
    """
    Re-keys `events` per-partition state saved by versions <= 0.0.77.

    Those versions keyed each partition as `{"grant_id", "calendar_id"}`. The stream now reads
    each grant's own calendars, so the grant lives in the calendar partition's `parent_slice`.
    Without re-keying, saved cursors would not match any partition and every calendar would
    resume from the newest cursor across all calendars instead of its own.
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return any("grant_id" in state.get("partition", {}) for state in (stream_state or {}).get("states", []))

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        return {**stream_state, "states": [self._rekey(state) for state in stream_state["states"]]}

    @staticmethod
    def _rekey(state: Mapping[str, Any]) -> Mapping[str, Any]:
        partition = state.get("partition", {})
        if "grant_id" not in partition:
            return state
        return {
            **state,
            "partition": {
                "calendar_id": partition.get("calendar_id"),
                "parent_slice": {"grant_id": partition["grant_id"], "parent_slice": {}},
            },
        }
