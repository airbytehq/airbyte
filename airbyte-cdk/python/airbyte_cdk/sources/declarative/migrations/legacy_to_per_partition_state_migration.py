# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.models import DatetimeBasedCursor, SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ParentStreamConfig


def _is_already_migrated(stream_state: Mapping[str, Any]) -> bool:
    return "states" in stream_state


class LegacyToPerPartitionStateMigration(StateMigration):
    """
    Transforms the input state for per-partitioned streams from the legacy format to the low-code format.
    The cursor field and partition ID fields are automatically extracted from the stream's DatetimebasedCursor and SubstreamPartitionRouter.

    Example input state:
    {
    "13506132": {
      "last_changed": "2022-12-27T08:34:39+00:00"
    }
    Example output state:
    {
      "partition": {"id": "13506132"},
      "cursor": {"last_changed": "2022-12-27T08:34:39+00:00"}
    }
    """

    def __init__(
        self,
        partition_router: SubstreamPartitionRouter,
        cursor: DatetimeBasedCursor,
        config: Mapping[str, Any],
        parameters: Mapping[str, Any],
    ):
        self._partition_router = partition_router
        self._cursor = cursor
        self._config = config
        self._parameters = parameters
        self._partition_key_field = InterpolatedString.create(
            self._get_partition_field(self._partition_router), parameters=self._parameters
        ).eval(self._config)
        self._cursor_field = InterpolatedString.create(self._cursor.cursor_field, parameters=self._parameters).eval(self._config)

    def _get_partition_field(self, partition_router: SubstreamPartitionRouter) -> str:
        parent_stream_config = partition_router.parent_stream_configs[0]

        # Retrieve the partition field with a condition, as properties are returned as a dictionary for custom components.
        partition_field = (
            parent_stream_config.partition_field
            if isinstance(parent_stream_config, ParentStreamConfig)
            else parent_stream_config.get("partition_field")  # type: ignore # See above comment on why parent_stream_config might be a dict
        )

        return partition_field

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if _is_already_migrated(stream_state):
            return False

        # There is exactly one parent stream
        number_of_parent_streams = len(self._partition_router.parent_stream_configs)
        if number_of_parent_streams != 1:
            # There should be exactly one parent stream
            return False
        """
        The expected state format is
        "<parent_key_id>" : {
          "<cursor_field>" : "<cursor_value>"
        }
        """
        if stream_state:
            for key, value in stream_state.items():
                if isinstance(value, dict):
                    keys = list(value.keys())
                    if len(keys) != 1:
                        # The input partitioned state should only have one key
                        return False
                    if keys[0] != self._cursor_field:
                        # Unexpected key. Found {keys[0]}. Expected {self._cursor.cursor_field}
                        return False
        return True

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        states = [{"partition": {self._partition_key_field: key}, "cursor": value} for key, value in stream_state.items()]
        return {"states": states}
