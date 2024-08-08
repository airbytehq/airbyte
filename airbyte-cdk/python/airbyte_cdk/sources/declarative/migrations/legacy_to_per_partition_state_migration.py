# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping, Callable, Optional

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.models import DatetimeBasedCursor, SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.models.declarative_component_schema import ParentStreamConfig
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.parsers.component_constructor import ComponentConstructor
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SimpleRetriever as SimpleRetrieverModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import SubstreamPartitionRouter as SubstreamPartitionRouterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CustomPartitionRouter as CustomPartitionRouterModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import LegacyToPerPartitionStateMigration as LegacyToPerPartitionStateMigrationModel
from airbyte_cdk.sources.types import Config

from pydantic import BaseModel


def _is_already_migrated(stream_state: Mapping[str, Any]) -> bool:
    return "states" in stream_state


class LegacyToPerPartitionStateMigration(StateMigration, ComponentConstructor):
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

    @classmethod
    def resolve_dependencies(
        cls,
        model: LegacyToPerPartitionStateMigrationModel,
        config: Config,
        declarative_stream: DeclarativeStreamModel,
        dependency_constructor: Callable[[BaseModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        retriever = declarative_stream.retriever

        # VERIFY
        if not isinstance(retriever, SimpleRetrieverModel):
            raise ValueError(
                f"LegacyToPerPartitionStateMigrations can only be applied on a DeclarativeStream with a SimpleRetriever. Got {type(retriever)}"
            )

        partition_router = retriever.partition_router
        if not isinstance(partition_router, (SubstreamPartitionRouterModel, CustomPartitionRouterModel)):
            raise ValueError(
                f"LegacyToPerPartitionStateMigrations can only be applied on a SimpleRetriever with a Substream partition router. Got {type(partition_router)}"
            )
        if not hasattr(partition_router, "parent_stream_configs"):
            raise ValueError("LegacyToPerPartitionStateMigrations can only be applied with a parent stream configuration.")

        return {"partition_router": declarative_stream.retriever.partition_router, "cursor":declarative_stream.incremental_sync, "config": config, "parameters": declarative_stream.parameters}  # type: ignore # The retriever type was already checked

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
