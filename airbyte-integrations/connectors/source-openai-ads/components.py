# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


class PerEntityToGlobalCursorStateMigration(StateMigration):
    """
    Convert the per-entity conversions state written by 0.1.x into one cursor for the stream.

    0.1.x read conversions one entity at a time and saved
    `{"use_global_cursor": false, "states": [{"partition": {"entity_id": ...}, "cursor": {"date": ...}}], "state": {"date": ...}}`.
    The conversions streams now group entities, so the CDK forces a global cursor, but it switches back to per-partition
    tracking whenever the incoming state has `"use_global_cursor": false`. The new cursor is the saved global `state`, which
    is left unset when absent so the stream starts from its configured start date.
    """

    _CURSOR_FIELD = "date"

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool(stream_state) and "states" in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state
        migrated = {key: value for key, value in stream_state.items() if key != "states"}
        migrated["use_global_cursor"] = True
        global_cursor = self._global_cursor(stream_state)
        if global_cursor is None:
            migrated.pop("state", None)
        else:
            migrated["state"] = {self._CURSOR_FIELD: global_cursor}
        return migrated

    def _global_cursor(self, stream_state: Mapping[str, Any]) -> Optional[str]:
        saved = (stream_state.get("state") or {}).get(self._CURSOR_FIELD)
        return saved or None
