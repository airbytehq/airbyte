#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Optional

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
    def close_slice(self, stream_slice: StreamSlice, most_recent_record: Optional[Record]) -> None:
        """
        Update state based on the stream slice and the latest record. Note that `stream_slice.cursor_slice` and
        `last_record.associated_slice` are expected to be the same but we make it explicit here that `stream_slice` should be leveraged to
        update the state.

        :param stream_slice: slice to close
        :param last_record: the latest record we have received for the slice. This is important to consider because even if the cursor emits
          a slice, some APIs are not able to enforce the upper boundary. The outcome is that the last_record might have a higher cursor
          value than the slice upper boundary and if we want to reduce the duplication as much as possible, we need to consider the highest
          value between the internal cursor, the stream slice upper boundary and the record cursor value.
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

    @abstractmethod
    def should_be_synced(self, record: Record) -> bool:
        """
        Evaluating if a record should be synced allows for filtering and stop condition on pagination
        """

    @abstractmethod
    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        """
        Evaluating which record is greater in terms of cursor. This is used to avoid having to capture all the records to close a slice
        """
