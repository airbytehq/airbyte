from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString

from airbyte_cdk.sources.declarative.models import SubstreamPartitionRouter

from airbyte_cdk.sources.declarative.models import DatetimeBasedCursor


class LegacyToPerPartitionStateMigration(StateMigration):

    def __init__(self, partition_router: SubstreamPartitionRouter, cursor: DatetimeBasedCursor, config: Mapping[str, Any], parameters: Mapping[str, Any]):
        self._partition_router = partition_router
        self._cursor = cursor
        self._config = config
        self._parameters = parameters

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if self._is_already_migrated(stream_state):
            return False

        # There is exactly one parent stream
        number_of_parent_streams = len(self._partition_router.parent_stream_configs)
        if number_of_parent_streams != 1:
            raise ValueError(f"There should be exactly one parent stream. Found {number_of_parent_streams}")
        """
        The expected state format is 
        "<parent_key_id>" : {
          "<cursor_field>" : "<cursor_value>"
        }
        """
        cursor_field = self._cursor_field()
        if stream_state:
            for key, value in stream_state.items():
                if isinstance(value, dict):
                    keys = list(value.keys())
                    if len(keys) != 1:
                        raise ValueError(f"")
                    if keys[0] != cursor_field:
                        raise ValueError(f"Unexpected key. Found {keys[0]}. Expected {self._cursor.cursor_field}")

        return True

    def _cursor_field(self):
        cursor_field_raw = InterpolatedString.create(self._cursor.cursor_field, parameters=self._parameters)
        return cursor_field_raw.eval(self._config)

    def _partition_key(self):
        # FIXME: maybe needs to be interpolated?
        return self._partition_router.parent_stream_configs[0].parent_key


    def _is_already_migrated(self, stream_state: Mapping[str, Any]) -> bool:
        if "states" not in stream_state:
            return False
        states = stream_state["states"]
        for state in states:
            cursor_component = state.get("cursor")
            if not cursor_component:
                raise ValueError(f"Found unexpected state with missing cursor component {stream_state}")
            cursor_keys = list(cursor_component.keys())
            if len(cursor_keys) != 1:
                raise ValueError(f"There should be exactly one cursor field. Found {cursor_keys}")
            if cursor_keys[0] != self._cursor_field():
                raise ValueError(f"Input state has invalid cursor field. Expected {self._cursor_field()}. Got {cursor_keys[0]}")

            partition_component = state.get("partition")
            if not partition_component:
                raise ValueError(f"Found unexpected state with missing partition component {stream_state}")
            partition_keys = list(partition_component)
            if len(partition_keys) != 1:
                raise ValueError(f"There should be exactly one partition field. Found {partition_keys}")
            if partition_keys[0] != self._partition_key():
                raise ValueError(f"Input state has invalid partition key. Expected {self._partition_key()}. Got {partition_keys[0]}")

        return True

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        partition_key_field = self._partition_router.parent_stream_configs[0].parent_key
        states = [
            {"partition": {partition_key_field: key}, "cursor": value}
            for key, value in stream_state.items()
        ]
        return {"states": states}
