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
        Args:
            stream_state (StreamState): The state of the streams to be set.
        Format of the stream state should be:
        {
            "state": {
                "last_updated": "2023-05-27T00:00:00Z"
            },
            "parent_state": {
                "parent_stream_name": {
                    "last_updated": "2023-05-27T00:00:00Z"
                }
            },
            "lookback_window": 132
        }
        """
        if not stream_state:
            return

        lookback_window = stream_state.get("lookback_window")
        if lookback_window is not None:
            self._lookback_window = lookback_window
            self._inject_lookback_into_stream_cursor(lookback_window)

        state = stream_state.get("state")
        if state:
            self._stream_cursor.set_initial_state(state)

        # Set parent state for partition routers based on parent streams
        parent_state = stream_state.get("parent_state")
        if parent_state:
            self._partition_router.set_initial_state(parent_state)

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
