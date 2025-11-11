# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, Optional

from airbyte_cdk.sources.streams.checkpoint import Cursor
from airbyte_cdk.sources.types import Record, StreamSlice, StreamState


@dataclass
class ResumableFullRefreshCursor(Cursor):
    """
    Cursor that allows for the checkpointing of sync progress according to a synthetic cursor based on the pagination state
    of the stream. Resumable full refresh syncs are only intended to retain state in between sync attempts of the same job
    with the platform responsible for removing said state.
    """

    def __init__(self) -> None:
        self._cursor: StreamState = {}

    def get_stream_state(self) -> StreamState:
        return self._cursor

    def set_initial_state(self, stream_state: StreamState) -> None:
        self._cursor = stream_state

    def observe(self, stream_slice: StreamSlice, record: Record) -> None:
        """
        Resumable full refresh manages state using a page number so it does not need to update state by observing incoming records.
        """
        pass

    def close_slice(self, stream_slice: StreamSlice, *args: Any) -> None:
        self._cursor = stream_slice.cursor_slice

    def should_be_synced(self, record: Record) -> bool:
        """
        Unlike date-based cursors which filter out records outside slice boundaries, resumable full refresh records exist within pages
        that don't have filterable bounds. We should always return them.
        """
        return True

    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        # A top-level RFR cursor only manages the state of a single partition
        return self._cursor
