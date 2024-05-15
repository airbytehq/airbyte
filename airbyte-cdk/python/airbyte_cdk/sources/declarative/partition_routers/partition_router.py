#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass

from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer


@dataclass
class PartitionRouter(StreamSlicer):
    """
    Base class for partition routers.

    Methods:
        set_parent_state(stream_state): Set the state of the parent streams.
        get_parent_state(): Get the state of the parent streams.
    """

    def set_parent_state(self, stream_state):
        """
        Set the state of the parent streams.

        Args:
            stream_state: The state of the streams to be set. This method can be overridden by subclasses.
        """
        pass

    def get_parent_state(self):
        """
        Get the state of the parent streams.

        Returns:
            The current state of the parent streams. This method can be overridden by subclasses.
        """
        return None
