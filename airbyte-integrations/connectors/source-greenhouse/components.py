#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.legacy_to_per_partition_state_migration import LegacyToPerPartitionStateMigration
from airbyte_cdk.sources.declarative.types import Config


class GreenhouseStateMigration(LegacyToPerPartitionStateMigration):
    declarative_stream: DeclarativeStream
    config: Config

    def __init__(self, declarative_stream: DeclarativeStream, config: Config):
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
