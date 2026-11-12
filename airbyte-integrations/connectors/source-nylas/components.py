# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


class EventsPartitionStateMigration(StateMigration):
    """
    Moves `events` per-partition state to the partition shape produced when calendars are the only parent stream.

    The stream used to combine a grants router with a calendars router, which produced partitions shaped as
    `{"calendar_id": ..., "grant_id": ..., "parent_slice": {}}`. With calendars as the single parent, the grant
    is the calendar's own parent slice: `{"calendar_id": ..., "parent_slice": {"grant_id": ..., "parent_slice": {}}}`.
    Without this migration the saved cursors would no longer match any partition and every calendar would fall
    back to the global cursor.
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
