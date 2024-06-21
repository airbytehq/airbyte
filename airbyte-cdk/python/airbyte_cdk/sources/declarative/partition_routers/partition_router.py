#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

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

    @abstractmethod
    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Set the state of the parent streams.

        This method should only be implemented if the slicer is based on some parent stream and needs to read this stream
        incrementally using the state.

        Args:
            stream_state (StreamState): The state of the streams to be set. The expected format is a dictionary that includes
                                        'parent_state' which is a dictionary of parent state names to their corresponding state.
                Example:
                {
                    "parent_state": {
                        "parent_stream_name_1": { ... },
                        "parent_stream_name_2": { ... },
                        ...
                    }
                }
        """

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
