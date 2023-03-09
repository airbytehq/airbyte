#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, MutableMapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.stream_slicers import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice


@dataclass
class EventsSimpleRetriever(SimpleRetriever):
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
        )


@dataclass
class EventsCartesianProductStreamSlicer(CartesianProductStreamSlicer):
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

    def __post_init__(self, options: Mapping[str, Any]):
        self._cursor = {}
        self._options = options

    def get_stream_state(self) -> Mapping[str, Any]:
        return self._cursor or {}

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):

        if not last_record:
            # this is actually initial stream state from CLI
            self._cursor = stream_slice
            return

        project_id = str(stream_slice.get("project_id", ""))
        if project_id:
            current_cursor_value = self._cursor.get(project_id, {}).get("timestamp", "")
            new_cursor_value = last_record.get("timestamp", "")

            self._cursor[project_id] = {"timestamp": max(current_cursor_value, new_cursor_value)}

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        """Since each project has its own state, then we need to have a separate
        datetime slices for each project
        """

        slices = []

        project_slicer, datetime_slicer = self.stream_slicers

        # support of old style state: it contains only a single 'timestamp' field
        old_style_state = stream_state if "timestamp" in stream_state else {}

        for project_slice in project_slicer.stream_slices(sync_mode, stream_state):
            project_id = str(project_slice.get("project_id", ""))

            # use old_style_state if state does not contain states for each project
            project_state = stream_state.get(project_id, {}) or old_style_state

            # Each project should have own datetime slices depends on its state
            project_datetime_slices = datetime_slicer.stream_slices(sync_mode, project_state)

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
