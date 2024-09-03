# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.checkpoint import Cursor
from airbyte_cdk.sources.streams.checkpoint.per_partition_key_serializer import PerPartitionKeySerializer
from airbyte_cdk.sources.types import Record, StreamSlice, StreamState
from airbyte_cdk.utils import AirbyteTracedException

FULL_REFRESH_COMPLETE_STATE: Mapping[str, Any] = {"__ab_full_refresh_sync_complete": True}


@dataclass
class SubstreamResumableFullRefreshCursor(Cursor):
    def __init__(self) -> None:
        self._per_partition_state: MutableMapping[str, StreamState] = {}
        self._partition_serializer = PerPartitionKeySerializer()

    def get_stream_state(self) -> StreamState:
        states = []
        for partition_tuple, partition_state in self._per_partition_state.items():
            states.append(
                {
                    "partition": self._to_dict(partition_tuple),
                    "cursor": partition_state,
                }
            )
        state: dict[str, Any] = {"states": states}

        return state

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Set the initial state for the cursors.

        This method initializes the state for each partition cursor using the provided stream state.
        If a partition state is provided in the stream state, it will update the corresponding partition cursor with this state.

        To simplify processing and state management, we do not maintain the checkpointed state of the parent partitions.
        Instead, we are tracking whether a parent has already successfully synced on a prior attempt and skipping over it
        allowing the sync to continue making progress. And this works for RFR because the platform will dispose of this
        state on the next sync job.

        Args:
            stream_state (StreamState): The state of the streams to be set. The format of the stream state should be:
                {
                    "states": [
                        {
                            "partition": {
                                "partition_key": "value_0"
                            },
                            "cursor": {
                                "__ab_full_refresh_sync_complete": True
                            }
                        },
                        {
                            "partition": {
                                "partition_key": "value_1"
                            },
                            "cursor": {},
                        },
                    ]
                }
        """
        if not stream_state:
            return

        if "states" not in stream_state:
            raise AirbyteTracedException(
                internal_message=f"Could not sync parse the following state: {stream_state}",
                message="The state for is format invalid. Validate that the migration steps included a reset and that it was performed "
                "properly. Otherwise, please contact Airbyte support.",
                failure_type=FailureType.config_error,
            )

        for state in stream_state["states"]:
            self._per_partition_state[self._to_partition_key(state["partition"])] = state["cursor"]

    def observe(self, stream_slice: StreamSlice, record: Record) -> None:
        """
        Substream resumable full refresh manages state by closing the slice after syncing a parent so observe is not used.
        """
        pass

    def close_slice(self, stream_slice: StreamSlice, *args: Any) -> None:
        self._per_partition_state[self._to_partition_key(stream_slice.partition)] = FULL_REFRESH_COMPLETE_STATE

    def should_be_synced(self, record: Record) -> bool:
        """
        Unlike date-based cursors which filter out records outside slice boundaries, resumable full refresh records exist within pages
        that don't have filterable bounds. We should always return them.
        """
        return True

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        """
        RFR record don't have ordering to be compared between one another.
        """
        return False

    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        if not stream_slice:
            raise ValueError("A partition needs to be provided in order to extract a state")

        return self._per_partition_state.get(self._to_partition_key(stream_slice.partition))

    def _to_partition_key(self, partition: Mapping[str, Any]) -> str:
        return self._partition_serializer.to_partition_key(partition)

    def _to_dict(self, partition_key: str) -> Mapping[str, Any]:
        return self._partition_serializer.to_partition(partition_key)
