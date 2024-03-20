from typing import Any, Mapping

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.models import DatetimeBasedCursor, SubstreamPartitionRouter


def _is_already_migrated(stream_state: Mapping[str, Any]) -> bool:
    return "states" in stream_state


class LegacyToPerPartitionStateMigration(StateMigration):
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

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if _is_already_migrated(stream_state):
            return False

        # There is exactly one parent stream
        number_of_parent_streams = len(self._partition_router.parent_stream_configs)
        if number_of_parent_streams != 1:
            # f"There should be exactly one parent stream
            return False
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
                        # The input partitioned state should only have one key
                        return False
                    if keys[0] != cursor_field:
                        # Unexpected key. Found {keys[0]}. Expected {self._cursor.cursor_field}
                        return False
        return True

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        partition_key_field = self._eval_partition_key()
        states = [{"partition": {partition_key_field: key}, "cursor": value} for key, value in stream_state.items()]
        return {"states": states}

    def _cursor_field(self) -> str:
        cursor_field = InterpolatedString.create(self._cursor.cursor_field, parameters=self._parameters)
        return str(cursor_field.eval(self._config))

    def _eval_partition_key(self) -> str:
        # FIXME: maybe needs to be interpolated?
        partition_key = InterpolatedString.create(self._partition_router.parent_stream_configs[0].parent_key, parameters=self._parameters)
        return str(partition_key.eval(self._config))
