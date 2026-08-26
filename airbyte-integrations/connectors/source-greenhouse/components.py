#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.types import Config


class ApplicationCursorStateMigration(StateMigration):
    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return self._contains_applied_at(stream_state)

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self._contains_applied_at(stream_state):
            return stream_state
        return self._drop_applied_at(stream_state)

    @classmethod
    def _contains_applied_at(cls, value: Any) -> bool:
        if isinstance(value, Mapping):
            return "applied_at" in value or any(cls._contains_applied_at(item) for item in value.values())
        if isinstance(value, list):
            return any(cls._contains_applied_at(item) for item in value)
        return False

    @classmethod
    def _drop_applied_at(cls, value: Any) -> Any:
        if isinstance(value, Mapping):
            return {key: cls._drop_applied_at(item) for key, item in value.items() if key != "applied_at"}
        if isinstance(value, list):
            return [cls._drop_applied_at(item) for item in value]
        return value


class PerPartitionToFlatStateMigration(StateMigration):
    """Collapse per-partition state onto a flat cursor for a collection endpoint."""

    declarative_stream: DeclarativeStreamModel
    config: Config

    _RESERVED = ("states", "state", "use_global_cursor", "lookback_window", "parent_state")

    def __init__(self, declarative_stream: DeclarativeStreamModel, config: Config):
        self._cursor_field = InterpolatedString.create(
            declarative_stream.incremental_sync.cursor_field, parameters=declarative_stream.parameters
        ).eval(config)

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool(stream_state) and self._cursor_field not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state
        cursors = list(self._collect_cursors(stream_state))
        return {self._cursor_field: min(cursors)} if cursors else {}

    def _collect_cursors(self, stream_state: Mapping[str, Any]) -> Any:
        for entry in stream_state.get("states", []):
            value = (entry.get("cursor") or {}).get(self._cursor_field)
            if value:
                yield value
        global_cursor = (stream_state.get("state") or {}).get(self._cursor_field)
        if global_cursor:
            yield global_cursor
        for key, value in stream_state.items():
            if key not in self._RESERVED and isinstance(value, Mapping) and value.get(self._cursor_field):
                yield value[self._cursor_field]
