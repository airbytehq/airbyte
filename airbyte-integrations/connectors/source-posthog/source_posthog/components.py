#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
import logging
import re

from airbyte_cdk.sources.declarative.incremental import Cursor
from airbyte_cdk.sources.declarative.retrievers import Retriever
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.stream_slicers import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
import requests

logger = logging.getLogger("airbyte")


# =============================================================================
# Original Events Stream Components (uses deprecated /events endpoint)
# =============================================================================

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


# =============================================================================
# Events V2 Stream Components (uses Query API with HogQL)
# =============================================================================

@dataclass
class EventsV2CartesianProductStreamSlicer(Cursor, CartesianProductStreamSlicer):
    """Stream slicer for events_v2 that supports project_id from config.

    This is needed for project-scoped personal API keys that cannot call
    the /api/projects endpoint to list projects.
    """

    config: Config = field(default_factory=dict)

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
        """Generate datetime slices for each project."""
        slices = []

        project_slicer, datetime_slicer = self.stream_slicers
        old_style_state = self._cursor if "timestamp" in self._cursor else {}

        # Check if project_id is provided in config (for project-scoped API keys)
        config_project_id = self.config.get("project_id") if self.config else None

        if config_project_id:
            # Use the project_id from config directly
            project_slices_iter = [{"project_id": str(config_project_id)}]
        else:
            # Fall back to fetching projects from API
            project_slices_iter = project_slicer.stream_slices()

        for project_slice in project_slices_iter:
            project_id = str(project_slice.get("project_id", ""))
            project_state = self._cursor.get(project_id, {}) or old_style_state

            datetime_slicer.set_initial_state(project_state)
            project_datetime_slices = datetime_slicer.stream_slices()

            if project_datetime_slices and project_state:
                project_datetime_slices[0]["start_time"] = project_state["timestamp"]
            for i, datetime_slice in enumerate(project_datetime_slices[1:], start=1):
                datetime_slice["start_time"] = project_datetime_slices[i - 1]["end_time"]

            for datetime_slice in project_datetime_slices:
                datetime_slice["project_id"] = project_id

            slices.extend(project_datetime_slices)

        return slices

    def should_be_synced(self, record: Record) -> bool:
        return True

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        first_cursor_value = first.get("timestamp")
        second_cursor_value = second.get("timestamp")
        if first_cursor_value and second_cursor_value:
            return first_cursor_value >= second_cursor_value
        elif first_cursor_value:
            return True
        else:
            return False


@dataclass
class EventsV2Retriever(Retriever):
    """
    Custom retriever for PostHog's Query API (events_v2 stream).

    Uses HogQL queries via POST to /api/projects/{project_id}/query/ endpoint.
    This replaces the deprecated /events endpoint with better performance and
    more flexible querying capabilities.

    Features:
    - Makes POST requests with HogQL queries
    - Transforms columnar response format to row objects
    - Handles pagination via OFFSET in the query
    - Joins with persons table for person data
    - Supports project-scoped personal API keys via project_id config
    """

    config: Config
    stream_slicer: Any  # Will be set by the declarative framework
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self._page_size = 10000
        self._field_mappings = {"uuid": "id"}  # Map uuid to id for consistency
        self._state: MutableMapping[str, Any] = {}

    @property
    def state(self) -> MutableMapping[str, Any]:
        if self.stream_slicer and hasattr(self.stream_slicer, 'get_stream_state'):
            return self.stream_slicer.get_stream_state()
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        if self.stream_slicer and hasattr(self.stream_slicer, 'set_initial_state'):
            self.stream_slicer.set_initial_state(value)
        self._state = value

    def _get_base_url(self) -> str:
        return self.config.get("base_url", "https://app.posthog.com")

    def _get_api_key(self) -> str:
        return self.config.get("api_key", "")

    def _validate_datetime(self, dt_str: str) -> str:
        """Validate datetime string format to prevent HogQL injection."""
        if not dt_str:
            raise ValueError("Empty datetime string")
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:?\d{2}|Z)?$'
        if not re.match(pattern, dt_str):
            raise ValueError(f"Invalid datetime format: {dt_str}")
        return dt_str

    def _build_hogql_query(self, stream_slice: StreamSlice, offset: int = 0) -> str:
        """Build the HogQL query for fetching events.

        Joins with persons table to get person properties and is_identified.
        """
        start_time = self._validate_datetime(stream_slice.get("start_time", ""))
        end_time = self._validate_datetime(stream_slice.get("end_time", ""))

        return f"""
            SELECT
                e.uuid,
                e.event,
                e.properties,
                e.timestamp,
                e.distinct_id,
                e.elements_chain,
                e.created_at,
                e.person.id as person_id,
                p.properties as person_properties,
                p.is_identified as person_is_identified
            FROM events e
            LEFT JOIN persons p ON p.id = e.person.id
            WHERE e.timestamp >= toDateTime('{start_time}')
              AND e.timestamp < toDateTime('{end_time}')
            ORDER BY e.timestamp ASC
            LIMIT {self._page_size}
            OFFSET {offset}
        """.strip()

    def _extract_records_from_response(self, response_body: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        """Transform columnar response to row objects with nested person object."""
        columns = response_body.get("columns", [])
        results = response_body.get("results", [])

        if not columns or not results:
            return []

        records = []
        for row in results:
            record = {}
            person_data = {}

            for i, col_name in enumerate(columns):
                if i < len(row):
                    value = row[i]

                    if col_name == "person_id":
                        person_data["id"] = value
                    elif col_name == "person_properties":
                        person_data["properties"] = value or {}
                    elif col_name == "person_is_identified":
                        person_data["is_identified"] = bool(value) if value is not None else False
                    else:
                        output_field = self._field_mappings.get(col_name, col_name)
                        record[output_field] = value

            if "distinct_id" in record:
                person_data["distinct_ids"] = [record["distinct_id"]]

            if person_data:
                record["person"] = person_data

            records.append(record)

        return records

    def stream_slices(self) -> Iterable[Optional[StreamSlice]]:
        """Delegate stream slicing to the configured stream_slicer."""
        if self.stream_slicer:
            yield from self.stream_slicer.stream_slices()
        else:
            yield None

    def read_records(
        self,
        records_schema_or_sync_mode: Any = None,
        stream_slice: Optional[StreamSlice] = None,
        stream_state: Optional[StreamState] = None,
        **kwargs,
    ) -> Iterable[Mapping[str, Any]]:
        """Read records from the Query API with pagination."""
        if not stream_slice:
            return

        project_id = stream_slice.get("project_id", "")
        if not project_id:
            logger.warning("No project_id in stream_slice, skipping")
            return

        offset = 0
        most_recent_record: Optional[Mapping[str, Any]] = None

        while True:
            hogql_query = self._build_hogql_query(stream_slice, offset)
            query_body = {
                "query": {
                    "kind": "HogQLQuery",
                    "query": hogql_query
                }
            }

            url = f"{self._get_base_url()}/api/projects/{project_id}/query/"
            headers = {
                "Authorization": f"Bearer {self._get_api_key()}",
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(url, json=query_body, headers=headers, timeout=300)
                response.raise_for_status()
                response_body = response.json()

                records = self._extract_records_from_response(response_body)

                for record in records:
                    yield record

                if records:
                    most_recent_record = records[-1]

                has_more = response_body.get("hasMore", len(records) == self._page_size)
                if not has_more or len(records) < self._page_size:
                    break

                offset += self._page_size

            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching events from Query API: {e}")
                raise

        if most_recent_record and self.stream_slicer and hasattr(self.stream_slicer, 'close_slice'):
            self.stream_slicer.close_slice(stream_slice, most_recent_record)
