# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
from dataclasses import InitVar, dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.legacy_to_per_partition_state_migration import LegacyToPerPartitionStateMigration
from airbyte_cdk.sources.declarative.models import (
    CustomIncrementalSync,
    DatetimeBasedCursor,
    ParentStreamConfig,
    SubstreamPartitionRouter,
)


@dataclass
class LegacyToPerPartitionStateMigrationWithParentSlice(LegacyToPerPartitionStateMigration):
    partition_router: SubstreamPartitionRouter
    cursor: CustomIncrementalSync | DatetimeBasedCursor
    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]]

    _partition_router: SubstreamPartitionRouter
    _cursor = CustomIncrementalSync | DatetimeBasedCursor
    _config: Mapping[str, Any]
    _parameters: InitVar[Mapping[str, Any]]
    _partition_key_field: str
    _cursor_field: str

    def __init__(
        self,
        partition_router: SubstreamPartitionRouter,
        cursor: CustomIncrementalSync | DatetimeBasedCursor,
        config: Mapping[str, Any],
        parameters: Mapping[str, Any],
    ):
        super().__init__(partition_router, cursor, config, parameters)

    def _get_partition_field(self, partition_router: SubstreamPartitionRouter) -> str:
        parent_stream_config = partition_router.parent_stream_configs[0]

        # Retrieve the partition field with a condition, as properties are returned as a dictionary for custom components.
        partition_field = (
            parent_stream_config.partition_field
            if not isinstance(parent_stream_config, dict)
            else parent_stream_config.get("partition_field")  # type: ignore # See above comment on why parent_stream_config might be a dict
        )

        return partition_field

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Uses super.migrate() to migrate the state from legacy to per partition state.
        Later we used the partition router to update the parent slice in the migrated state partition.
        This is because old state format didn't keep the parent slice in the partition.

        After manifest migration completes for all connections this can be removed as the state will keep the parent slice in the partition
        and the passed states to this component will not pass the self.should_migrate() check as the state will be already migrated.
        """
        migrated_states = super().migrate(stream_state)

        if not hasattr(self._partition_router, "stream_slices"):
            # If the partition router does not have stream_slices, return the states as is
            return migrated_states

        migrated_states_partitions_map = {}
        for migrated_state in migrated_states["states"]:
            migrated_state_partition = migrated_state["partition"]
            migrated_partition_value = migrated_state_partition[self._partition_key_field]
            migrated_states_partitions_map[migrated_partition_value] = migrated_state_partition

        for partition_router_stream_slice in self._partition_router.stream_slices():  # type: ignore # See above comment on why parent_stream_config might be a dict
            partition_router_stream_slice_partition_parent_slice = partition_router_stream_slice.partition["parent_slice"]
            partition_router_stream_slice_partition_value = partition_router_stream_slice.partition[self._partition_key_field]
            if migrated_states_partitions_map.get(partition_router_stream_slice_partition_value):
                # If the partition router stream slice partition value exists in the migrated states partitions map, then
                # update the parent slice in the migrated state partition, I'm making it safe as there could be a minimal
                # chance that a new partition is created since the last state save.
                migrated_state_partition = migrated_states_partitions_map[partition_router_stream_slice_partition_value]
                migrated_state_partition["parent_slice"] = partition_router_stream_slice_partition_parent_slice
                # Remove the partition from the map so we can check that all of them were migrated
                del migrated_states_partitions_map[partition_router_stream_slice_partition_value]

        if migrated_states_partitions_map:
            raise ValueError(f"Some partitions were not migrated: {migrated_states_partitions_map}")

        return migrated_states
