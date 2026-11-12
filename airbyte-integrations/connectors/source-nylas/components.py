# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


class EventsPartitionStateMigration(StateMigration):
    """
    Re-keys `events` per-partition state saved before the stream was partitioned by calendar only.

    Older versions keyed each partition as `{"grant_id": ..., "calendar_id": ..., "parent_slice": {}}`.
    The stream now nests the grant under the calendar's parent slice:
    `{"calendar_id": ..., "parent_slice": {"grant_id": ..., "parent_slice": {}}}`.
    Without the re-key, each calendar would lose its own cursor and resume from the stream-wide one.
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return any(self._is_legacy(state.get("partition")) for state in stream_state.get("states") or [])

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        states = []
        for state in stream_state.get("states") or []:
            partition = state.get("partition")
            if self._is_legacy(partition):
                partition = {
                    "calendar_id": partition["calendar_id"],
                    "parent_slice": {"grant_id": partition["grant_id"], "parent_slice": {}},
                }
            states.append({**state, "partition": partition})
        return {**stream_state, "states": states}

    @staticmethod
    def _is_legacy(partition: Any) -> bool:
        return isinstance(partition, Mapping) and "grant_id" in partition and "calendar_id" in partition
