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
        get_stream_state(): Get the state of the parent streams.
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
