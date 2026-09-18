#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import InitVar, dataclass
from datetime import timedelta, timezone
from typing import Any, Iterable, Mapping, Optional
from urllib.parse import parse_qsl, urljoin, urlsplit
from uuid import UUID

from dateutil.parser import isoparse
from requests.adapters import HTTPAdapter

from airbyte_cdk.sources.declarative.incremental import Cursor
from airbyte_cdk.sources.declarative.requesters.paginators.default_paginator import DefaultPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.stream_slicers import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState


class PosthogHTTPAdapter(HTTPAdapter):
    timeout = (30, 120)

    def send(self, request, **kwargs):
        if kwargs.get("timeout") is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


@dataclass
class PosthogNextPageStrategy(PaginationStrategy):
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters):
        self.reset()

    @property
    def initial_token(self):
        return None

    def get_page_size(self):
        return None

    def reset(self):
        self._seen = set()

    @staticmethod
    def _page_key(url):
        parts = urlsplit(url)
        return (parts.path.rstrip("/"), tuple(sorted(parse_qsl(parts.query))))

    def next_page_token(self, response, last_records):
        next_url = response.json().get("next")
        if not next_url:
            return None
        next_url = urljoin(response.url, next_url)
        current, target = urlsplit(response.url), urlsplit(next_url)
        if (target.scheme, target.netloc, target.path.rstrip("/")) != (current.scheme, current.netloc, current.path.rstrip("/")):
            raise ValueError("PostHog returned a next-page URL outside the current endpoint")
        self._seen.add(self._page_key(response.url))
        key = self._page_key(next_url)
        if key in self._seen:
            raise ValueError("PostHog repeated a pagination cursor; stopping to avoid an endless sync")
        self._seen.add(key)
        return next_url


@dataclass
class PosthogRetriever(SimpleRetriever):
    def __post_init__(self, parameters):
        super().__post_init__(parameters)
        self.cursor = self.stream_slicer if isinstance(self.stream_slicer, Cursor) else None

    def _request_params(self, stream_state=None, stream_slice=None, next_page_token=None):
        # The next URL already contains the complete query, including event time bounds.
        if next_page_token:
            return {}
        params = dict(super()._request_params(stream_state, stream_slice, next_page_token))
        if isinstance(self.paginator, DefaultPaginator):
            params["limit"] = self.config.get("persons_page_size", 1000) if self.name == "persons" else 100
        return params


@dataclass
class EventsRetriever(PosthogRetriever):
    def _fetch_next_page(self, stream_state, stream_slice, next_page_token=None):
        self._event_page_token = next_page_token
        return super()._fetch_next_page(stream_state, stream_slice, next_page_token)

    @staticmethod
    def _timestamp(value):
        parsed = isoparse(value)
        if parsed.tzinfo is None:
            raise ValueError("PostHog returned an event timestamp without a timezone")
        return parsed.astimezone(timezone.utc)

    @classmethod
    def _key(cls, record):
        event_id = UUID(record["id"]).int
        # ClickHouse UUID ordering compares the second 64-bit half first.
        return (cls._timestamp(record["timestamp"]), event_id & ((1 << 64) - 1), event_id >> 64)

    def _request_params(self, stream_state=None, stream_slice=None, next_page_token=None):
        params = dict(SimpleRetriever._request_params(self, stream_state, stream_slice, None))
        start = self._timestamp(stream_slice["start_time"])
        params.update(
            limit=1000,
            orderBy=json.dumps(["timestamp", "uuid"]),
            # REST bounds are exclusive; include the start of each half-open slice.
            after=(start - timedelta(microseconds=1)).isoformat(timespec="microseconds"),
            before=stream_slice["end_time"],
        )
        if next_page_token:
            timestamp = self._timestamp(next_page_token["timestamp"]).isoformat(timespec="microseconds")
            event_id = str(UUID(next_page_token["id"]))
            bound = f"toDateTime('{timestamp}')"
            predicate = f"timestamp > {bound} OR (timestamp = {bound} AND uuid > toUUID('{event_id}'))"
            params["properties"] = json.dumps([{"type": "hogql", "key": predicate}])
        return params

    def _parse_response(self, response, stream_state, records_schema, stream_slice=None, next_page_token=None):
        if response is not None:
            payload = response.json()
            if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
                raise ValueError("PostHog returned an invalid events page")
        records = list(super()._parse_response(response, stream_state, records_schema, stream_slice, next_page_token))
        boundary = self._key(self._event_page_token) if self._event_page_token else None
        previous = None
        start, end = self._timestamp(stream_slice["start_time"]), self._timestamp(stream_slice["end_time"])
        for record in records:
            key = self._key(record)
            if not start <= key[0] < end:
                raise ValueError("PostHog returned an event outside the requested slice")
            if boundary is not None and key <= boundary:
                raise ValueError("PostHog event page did not advance beyond the requested timestamp/UUID cursor")
            if previous is not None and key < previous:
                field = "timestamp" if key[0] < previous[0] else "UUID"
                raise ValueError(f"PostHog event page reversed {field} order within the page")
            previous = key
        return records

    def _next_page_token(self, response):
        # Legacy `next` loses tied timestamps and can be null before the range is exhausted.
        records = self._records_from_last_response
        return {"timestamp": records[-1]["timestamp"], "id": records[-1]["id"]} if records else None


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
            current_cursor_value = self._cursor.get(project_id, {}).get("timestamp", self._cursor.get("timestamp", ""))
            new_cursor_value = most_recent_record.get("timestamp", "")

            self._cursor[project_id] = {"timestamp": max(filter(None, (current_cursor_value, new_cursor_value)), key=isoparse)}

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
            lookback_hours = datetime_slicer.config.get("events_lookback_hours", 0)
            if project_state and lookback_hours:
                start = datetime_slicer.start_datetime.get_datetime(datetime_slicer.config)
                replay_from = max(start, isoparse(project_state["timestamp"]) - timedelta(hours=lookback_hours))
                project_state = {"timestamp": replay_from.isoformat(timespec="microseconds")}

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
            return isoparse(first_cursor_value) >= isoparse(second_cursor_value)
        elif first_cursor_value:
            return True
        else:
            return False
