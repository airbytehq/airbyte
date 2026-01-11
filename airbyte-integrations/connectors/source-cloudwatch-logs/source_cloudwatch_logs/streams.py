#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime as dt
import logging
from functools import lru_cache
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
)

import boto3
from airbyte_protocol_dataclasses.models.airbyte_protocol import SyncMode
from dateutil import parser

from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.core import StreamData


class Logs(Stream, IncrementalMixin):
    """
    A CloudWatch log group stream that supports incremental sync based on log
    event timestamps.
    """

    cursor_field = "timestamp"
    _cursor_value = None
    primary_key = None

    def __init__(
        self,
        region_name: str,
        log_group_name: str,
        session: boto3.Session,
        name: Optional[str] = None,
        log_stream_names: Optional[List[str]] = None,
        filter_pattern: Optional[str] = None,
        start_date: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.region_name = region_name
        self.log_group_name = log_group_name
        self.start_date = int(parser.parse(start_date).timestamp() * 1000) if start_date else None
        self.client = session.client("logs")
        self._name = name
        self.kwargs: Dict[str, Any] = {}
        if log_stream_names:
            self.kwargs["logStreamNames"] = log_stream_names
        if filter_pattern:
            self.kwargs["filterPattern"] = filter_pattern

        self._logger = logging.getLogger(f"airbyte.source.cloudwatch.{log_group_name}")
        self._logger.debug(f"Querying logs with parameters: {self.kwargs}")

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        return self.log_group_name

    def stream_slices(
        self,
        *,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        stream_state = stream_state or {}

        last_state = stream_state.get(self.cursor_field)
        if last_state:
            start_timestamp = last_state
        elif self.start_date:
            start_timestamp = self.start_date
        else:
            start_timestamp = self._get_start_timestamp()

        if not start_timestamp:
            return []

        # Create 1-day slices between beginning of the log group and now
        current_time = int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)  # milliseconds
        one_day_ms = 24 * 60 * 60 * 1000
        return [
            {
                "start_time": ts,
                "end_time": min(ts + one_day_ms - 1, current_time),
            }
            for ts in range(start_timestamp, current_time + 1, one_day_ms)
        ]

    def _get_start_timestamp(self) -> Optional[int]:
        response = self.client.filter_log_events(
            logGroupName=self.log_group_name,
            startTime=0,
            limit=1,
            **self.kwargs,
        )
        events = response.get("events", [])
        if events:
            earliest_timestamp: int = events[0]["timestamp"]
            self.logger.info(f"Earliest log event timestamp: {earliest_timestamp}")
            return earliest_timestamp
        else:
            return None

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        """The base JSON schema for CloudWatch logs."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "timestamp": {"type": "integer"},
                "message": {"type": "string"},
                "logStreamName": {"type": "string"},
                "ingestionTime": {"type": "integer"},
                "eventId": {"type": "string"},
            },
        }

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        stream_slice = stream_slice or {}

        start_time = stream_slice.get("start_time", 0)
        end_time = stream_slice.get("end_time")
        self._logger.info(f"Fetching logs from: {start_time} to {end_time} for group: {self.log_group_name}")

        next_token = None
        while True:
            params = {
                "logGroupName": self.log_group_name,
                "startTime": start_time,
                "endTime": end_time,
                "limit": 10000,
            }
            self.logger.debug(f"Fetching log events with parameters: {params}")

            if next_token:
                params["nextToken"] = next_token

            response = self.client.filter_log_events(**params, **self.kwargs)
            events = response.get("events", [])

            for event in events:
                if self._cursor_value is None:
                    self._cursor_value = event[self.cursor_field]
                else:
                    self._cursor_value = max(event[self.cursor_field], self._cursor_value)
                yield event

            next_token = response.get("nextToken")
            if not next_token:
                break

    @property
    def state(self) -> MutableMapping[str, Any]:
        if self._cursor_value is not None:
            return {self.cursor_field: self._cursor_value}
        return {}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value.get(self.cursor_field)
