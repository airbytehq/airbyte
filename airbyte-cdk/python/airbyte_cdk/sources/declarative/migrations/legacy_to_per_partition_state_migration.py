from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString


class LegacyToPerPartitionStateMigration(StateMigration):

    def __init__(self, partition_router, cursor, config, parameters):
        self._partition_router = partition_router
        self._cursor = cursor
        self._config = config
        self._parameters = parameters

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
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
        cursor_field_raw = InterpolatedString.create(self._cursor.cursor_field, parameters=self._parameters)
        cursor_field_evaluated = cursor_field_raw.eval(self._config)
        if stream_state:
            for key, value in stream_state.items():
                if isinstance(value, dict):
                    keys = list(value.keys())
                    if len(keys) != 1:
                        raise ValueError(f"")
                    if keys[0] != cursor_field_evaluated:
                        raise ValueError(f"Unexpected key. Found {keys[0]}. Expected {self._cursor.cursor_field}")
                print(f"value: {value}")


        return True

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        partition_key_field = self._partition_router.parent_stream_configs[0].parent_key
        states = [
            {"partition": {partition_key_field: key}, "cursor": value}
            for key, value in stream_state.items()
        ]
        return {"states": states}
