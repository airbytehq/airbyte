#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass
from typing import Mapping, Optional

from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.types import StreamState


@dataclass
class PartitionRouter(StreamSlicer):
    """
    Base class for partition routers.
    Methods:
        set_parent_state(stream_state): Set the state of the parent streams.
        get_parent_state(): Get the state of the parent streams.
    """

    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Set the initial state for the cursors.

        This method initializes the state for each partition cursor using the provided stream state.
        If a partition state is provided in the stream state, it will update the corresponding partition cursor with this state.

        Additionally, it sets the parent state for partition routers that are based on parent streams. If a partition router
        does not have parent streams, this step will be skipped due to the default PartitionRouter implementation.

        Args:
            stream_state (StreamState): The state of the streams to be set. The format of the stream state should be:
                {
                    "states": [
                        {
                            "partition": {
                                "partition_key": "value"
                            },
                            "cursor": {
                                "last_updated": "2023-05-27T00:00:00Z"
                            }
                        }
                    ],
                    "parent_state": {
                        "parent_stream_name": {
                            "last_updated": "2023-05-27T00:00:00Z"
                        }
                    }
                }
        """
        if not stream_state:
            return

        state_dict = stream_state.get("states")
        if state_dict is None:
            self._state_to_migrate_from = stream_state
        else:
            # Avoid recomputing the partition key by using a set comprehension for optimizing.
            partitions = {self._to_partition_key(state["partition"]): state["cursor"] for state in state_dict}
            self._cursor_per_partition.update({key: self._create_cursor(state) for key, state in partitions.items()})

        self._partition_router.set_initial_state(stream_state)

    @abstractmethod
    def get_stream_state(self) -> Optional[Mapping[str, StreamState]]:
        """
        Get the state of the parent streams.

        This method should only be implemented if the slicer is based on some parent stream and needs to read this stream
        incrementally using the state.

        Returns:
            Optional[Mapping[str, StreamState]]: The current state of the parent streams in a dictionary format.
                 The returned format will be:
                 {
                     "parent_stream_name1": {
                         "last_updated": "2023-05-27T00:00:00Z"
                     },
                     "parent_stream_name2": {
                         "last_updated": "2023-05-27T00:00:00Z"
                     }
                 }
        """
