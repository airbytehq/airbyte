#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod

from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class Cursor(ABC, StreamSlicer):
    """
    Cursors are components that allow for incremental syncs. They keep track of what data has been consumed and slices the requests based on
    that information.
    """

    @abstractmethod
    def set_initial_state(self, stream_state: StreamState) -> None:
        """
        Cursors are not initialized with their state. As state is needed in order to function properly, this method should be called
        before calling anything else

        :param stream_state: The state of the stream as returned by get_stream_state
        """

    @abstractmethod
    def update_state(self, stream_slice: StreamSlice, last_record: Record) -> None:
        """
        Update state based on the latest record

        :param stream_slice: Current stream_slice
        :param last_record: Last record read from the source
        """

    @abstractmethod
    def get_stream_state(self) -> StreamState:
        """
        Returns the current stream state. We would like to restrict it's usage since it does expose internal of state. As of 2023-06-14, it
        is used for two things:
        * Interpolation of the requests
        * Transformation of records
        * Saving the state

        For the first case, we are probably stuck with exposing the stream state. For the second, we can probably expose a method that
        allows for emitting the state to the platform.
        """
