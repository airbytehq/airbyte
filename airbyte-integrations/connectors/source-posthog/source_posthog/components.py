#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.sources.declarative.incremental import DeclarativeCursor
from airbyte_cdk.sources.declarative.stream_slicers import CartesianProductStreamSlicer
from airbyte_cdk.sources.types import Record, StreamSlice, StreamState


@dataclass
class EventsCartesianProductStreamSlicer(DeclarativeCursor, CartesianProductStreamSlicer):
    """Connector requires support of nested state - each project should have own timestamp value, like:
    {
        "project_id1": {
          "timestamp": "2021-02-01T10:21:35.003000Z"
        },
        "project_idX": {
          "timestamp": "2022-11-17:00:00.000000Z"
        }
    }
    we also have to support old-style (before 0.1.8) states, like:
    {
        "timestamp": "2021-17-01T10:21:35.003000Z"
    }

    Slicer also produces separate datetime slices for each project
    """

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._cursor = {}
        self._parameters = parameters

    def get_stream_state(self) -> Mapping[str, Any]:
        return self._cursor or {}

    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        """Return the cursor state for the project of the incoming slice (per-partition state)."""
        if not stream_slice:
            return self.get_stream_state()
        project_id = str(stream_slice.get("project_id", ""))
        return self._cursor.get(project_id, {})

    def set_initial_state(self, stream_state: StreamState) -> None:
        self._cursor = stream_state

    def close_slice(self, stream_slice: StreamSlice, most_recent_record: Optional[Record]) -> None:
        project_id = str(stream_slice.get("project_id", ""))
        if project_id and most_recent_record:
            current_cursor_value = self._cursor.get(project_id, {}).get("timestamp", "")
            new_cursor_value = most_recent_record.get("timestamp", "")

            self._cursor[project_id] = {"timestamp": max(current_cursor_value, new_cursor_value)}

    def stream_slices(self) -> Iterable[StreamSlice]:
        """Since each project has its own state, then we need to have a separate
        datetime slices for each project
        """

        slices = []

        project_slicer, datetime_slicer = self.stream_slicers

        # support of old style state: it contains only a single 'timestamp' field
        old_style_state = self._cursor if "timestamp" in self._cursor else {}

        for project_slice in project_slicer.stream_slices():
            project_id = str(project_slice.get("project_id", ""))

            # use old_style_state if state does not contain states for each project
            project_state = self._cursor.get(project_id, {}) or old_style_state

            # Each project should have own datetime slices depends on its state.
            # Copy each slice into a plain dict: StreamSlice is immutable, and the date
            # ranges are rewritten below to be contiguous.
            datetime_slicer.set_initial_state(project_state)
            project_datetime_slices = [dict(datetime_slice) for datetime_slice in datetime_slicer.stream_slices()]

            # fix date ranges: start_time of next slice must be equal to end_time of previous slice
            if project_datetime_slices and project_state:
                project_datetime_slices[0]["start_time"] = project_state["timestamp"]
            for i in range(1, len(project_datetime_slices)):
                project_datetime_slices[i]["start_time"] = project_datetime_slices[i - 1]["end_time"]

            # Add project id to each slice
            for datetime_slice in project_datetime_slices:
                slices.append(StreamSlice(partition={"project_id": project_id}, cursor_slice=datetime_slice))

        return slices

    def should_be_synced(self, record: Record) -> bool:
        """
        As of 2023-06-28, the expectation is that this method will only be used for semi-incremental and data feed and therefore the
        implementation is irrelevant for posthog
        """
        return True

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        """
        Evaluating which record is greater in terms of cursor. This is used to avoid having to capture all the records to close a slice
        """
        first_cursor_value = first.get("timestamp")
        second_cursor_value = second.get("timestamp")
        if first_cursor_value and second_cursor_value:
            return first_cursor_value >= second_cursor_value
        elif first_cursor_value:
            return True
        else:
            return False
