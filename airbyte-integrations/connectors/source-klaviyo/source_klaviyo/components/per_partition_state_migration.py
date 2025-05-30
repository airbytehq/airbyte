#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.types import Config


class PerPartitionToSingleStateMigration(StateMigration):
    """
    Transforms the input state for per-partitioned streams from the legacy format to the low-code format.
    The cursor field and partition ID fields are automatically extracted from the stream's DatetimebasedCursor and SubstreamPartitionRouter.

    Example input state:
    {
      "partition": {"event_id": "13506132"},
      "cursor": {"datetime": "2120-10-10 00:00:00+00:00"}
    }
    Example output state:
    {
      "datetime": "2120-10-10 00:00:00+00:00"
    }
    """

    declarative_stream: DeclarativeStream
    config: Config

    def __init__(self, declarative_stream: DeclarativeStream, config: Config):
        self._config = config
        self.declarative_stream = declarative_stream
        self._cursor = declarative_stream.incremental_sync
        self._parameters = declarative_stream.parameters
        self._cursor_field = InterpolatedString.create(self._cursor.cursor_field, parameters=self._parameters).eval(self._config)

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return "states" in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state

        min_state = min(stream_state.get("states"), key=lambda state: state["cursor"][self._cursor_field])
        return min_state.get("cursor")
