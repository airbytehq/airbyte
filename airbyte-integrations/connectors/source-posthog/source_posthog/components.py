#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.declarative.incremental import Cursor
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.stream_slicers import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


@dataclass
class EventsSimpleRetriever(SimpleRetriever):
    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters)
        self.cursor = self.stream_slicer if isinstance(self.stream_slicer, Cursor) else None

    def request_params(
        self,
        stream_state: StreamSlice,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        """Events API return records in descendent order (newest first).
        Default page limit is 100 items.

        Even though API mentions such pagination params as 'limit' and 'offset', they are actually ignored.
        Instead, response contains 'next' url with datetime range for next OLDER records, like:

        response:
        {
            "next": "https://app.posthog.com/api/projects/2331/events?after=2021-01-01T00%3A00%3A00.000000Z&before=2021-05-29T16%3A44%3A43.175000%2B00%3A00",
            "results": [
                {id ...},
                {id ...},
            ]
        }

        So if next_page_token is set (contains 'after'/'before' params),
        then stream_slice params ('after'/'before') should be ignored.
        """

        if next_page_token:
            stream_slice = {}

        return self._get_request_options(
            stream_slice,
            next_page_token,
            self.requester.get_request_params,
            self.paginator.get_request_params,
            self.stream_slicer.get_request_params,
            self.requester.get_authenticator().get_request_body_json,
        )


@dataclass
class EventsCartesianProductStreamSlicer(Cursor, CartesianProductStreamSlicer):
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

            # Each project should have own datetime slices depends on its state
            datetime_slicer.set_initial_state(project_state)
            project_datetime_slices = datetime_slicer.stream_slices()

            # fix date ranges: start_time of next slice must be equal to end_time of previous slice
            if project_datetime_slices and project_state:
                project_datetime_slices[0]["start_time"] = project_state["timestamp"]
            for i, datetime_slice in enumerate(project_datetime_slices[1:], start=1):
                datetime_slice["start_time"] = project_datetime_slices[i - 1]["end_time"]

            # Add project id to each slice
            for datetime_slice in project_datetime_slices:
                datetime_slice["project_id"] = project_id

            slices.extend(project_datetime_slices)

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
