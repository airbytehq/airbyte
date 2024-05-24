#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Optional

from airbyte_cdk.sources.types import Record, StreamSlice, StreamState


class Cursor(ABC):
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

    def observe(self, stream_slice: StreamSlice, record: Record) -> None:
        """
        Register a record with the cursor; the cursor instance can then use it to manage the state of the in-progress stream read.

        :param stream_slice: The current slice, which may or may not contain the most recently observed record
        :param record: the most recently-read record, which the cursor can use to update the stream state. Outwardly-visible changes to the
          stream state may need to be deferred depending on whether the source reliably orders records by the cursor field.
        """
        pass

    @abstractmethod
    def close_slice(self, stream_slice: StreamSlice, *args: Any) -> None:
        """
        Update state based on the stream slice. Note that `stream_slice.cursor_slice` and `most_recent_record.associated_slice` are expected
        to be the same but we make it explicit here that `stream_slice` should be leveraged to update the state. We do not pass in the
        latest record, since cursor instances should maintain the relevant internal state on their own.

        :param stream_slice: slice to close
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

    @abstractmethod
    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        """
        Get the state value of a specific stream_slice. For incremental or resumable full refresh cursors which only manage state in
        a single dimension this is the entire state object. For per-partition cursors used by substreams, this returns the state of
        a specific parent delineated by the incoming slice's partition object.
        """
