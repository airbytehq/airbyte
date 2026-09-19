#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


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
