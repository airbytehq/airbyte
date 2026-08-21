#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.legacy_to_per_partition_state_migration import LegacyToPerPartitionStateMigration
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.types import Config


class GreenhouseStateMigration(LegacyToPerPartitionStateMigration):
    declarative_stream: DeclarativeStreamModel
    config: Config

    def __init__(self, declarative_stream: DeclarativeStreamModel, config: Config):
        self._partition_router = declarative_stream.retriever.partition_router
        self._cursor = declarative_stream.incremental_sync
        self._config = config
        self._parameters = declarative_stream.parameters
        self._partition_key_field = InterpolatedString.create(
            self._get_partition_field(self._partition_router), parameters=self._parameters
        ).eval(self._config)
        self._cursor_field = InterpolatedString.create(self._cursor.cursor_field, parameters=self._parameters).eval(self._config)

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        LegacyToPerPartitionStateMigration migrates partition keys as string, while real type of id in greenhouse is integer,
        which leads to partition mismatch.
        To prevent this type casting for partition key was added.
        """
        states = [
            {"partition": {self._partition_key_field: int(key), "parent_slice": {}}, "cursor": value} for key, value in stream_state.items()
        ]
        return {"states": states}


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
