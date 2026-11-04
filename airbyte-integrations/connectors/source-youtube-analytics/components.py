#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import csv
import io
import math
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Generator, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qs, urlparse

import requests

from airbyte_cdk import AirbyteTracedException, Decoder, FailureType
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.types import StreamSlice, StreamState


@dataclass
class AnalyticsQueryRequester(HttpRequester):
    """Validate the optional channel query configuration without changing bulk requests."""

    request_parameters: Optional[Mapping[str, Any]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        settings = self.config.get("query_reports", {})
        try:
            if not isinstance(settings, Mapping):
                raise ValueError("query_reports must be an object")
            if self.config.get("content_owner_id"):
                raise ValueError("query_reports supports channel owners only; remove content_owner_id or disable query_reports")
            channel_id = settings.get("channel_id")
            if not isinstance(channel_id, str) or not channel_id.strip() or channel_id != channel_id.strip():
                raise ValueError("query_reports.channel_id must identify the authorized channel")
            for field in ("start_date", "end_date"):
                value = settings.get(field)
                if field == "end_date" and field not in settings:
                    continue
                if not isinstance(value, str) or datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d") != value:
                    raise ValueError(f"query_reports.{field} must use YYYY-MM-DD")
            if settings.get("end_date") and settings["end_date"] < settings["start_date"]:
                raise ValueError("query_reports.end_date must be on or after start_date")
            for field, default in (("lookback_days", 7), ("data_lag_days", 3)):
                value = settings.get(field, default)
                if type(value) is not int or value < 0:
                    raise ValueError(f"query_reports.{field} must be a nonnegative integer")
        except (TypeError, ValueError) as error:
            raise AirbyteTracedException(message=str(error), failure_type=FailureType.config_error) from error
        # The custom-component factory forwards annotated fields, but does not build the
        # standard request-options provider for a CustomRequester. Interpolate explicitly.
        self.request_options_provider = InterpolatedRequestOptionsProvider(
            config=self.config, parameters=parameters, request_parameters=self.request_parameters
        )
        super().__post_init__(parameters)


@dataclass
class AnalyticsQueryExtractor(RecordExtractor):
    """Decode a targeted query's positional rows using its returned column headers.

    The channel comes from the explicit request configuration, not an inferred video or
    bulk-report dimension. Validate the entire page before emitting any of its records.
    """

    config: Mapping[str, Any]

    METRICS = {
        "views": "INTEGER",
        "engagedViews": "INTEGER",
        "estimatedMinutesWatched": "FLOAT",
        "averageViewDuration": "FLOAT",
        "averageViewPercentage": "FLOAT",
        "likes": "INTEGER",
        "dislikes": "INTEGER",
        "comments": "INTEGER",
        "shares": "INTEGER",
        "subscribersGained": "INTEGER",
        "subscribersLost": "INTEGER",
        "videosAddedToPlaylists": "INTEGER",
        "videosRemovedFromPlaylists": "INTEGER",
    }

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        try:
            body = response.json()
            if not isinstance(body, dict) or "error" in body:
                raise ValueError("Expected a YouTube Analytics result table")
            headers = body.get("columnHeaders", [])
            names = [header["name"] for header in headers]
            expected = {"day": "STRING", **self.METRICS}
            if len(names) != len(set(names)) or set(names) != set(expected):
                raise ValueError("YouTube Analytics column headers do not match the channel daily report")
            for header in headers:
                name = header["name"]
                # YouTube can declare duration/watch-time measures as INTEGER or FLOAT.
                # Both fit the stream's number schema; counts must remain integer-valued.
                allowed_types = ("INTEGER", "FLOAT") if expected[name] == "FLOAT" else (expected[name],)
                if header.get("dataType") not in allowed_types or header.get("columnType") != ("DIMENSION" if name == "day" else "METRIC"):
                    raise ValueError(f"Unexpected YouTube Analytics column type for {name}")
            rows = body.get("rows", [])
            if not isinstance(rows, list):
                raise ValueError("YouTube Analytics rows must be an array")
            query = parse_qs(urlparse(response.request.url).query)
            start, end = query["startDate"][0], query["endDate"][0]
            records = []
            for row in rows:
                if not isinstance(row, list) or len(row) != len(names):
                    raise ValueError("YouTube Analytics row length does not match column headers")
                record = dict(zip(names, row))
                day = record["day"]
                if not isinstance(day, str) or datetime.strptime(day, "%Y-%m-%d").strftime("%Y-%m-%d") != day or not start <= day <= end:
                    raise ValueError("YouTube Analytics returned a day outside the requested date interval")
                for name, data_type in self.METRICS.items():
                    value = record[name]
                    if value is None:
                        continue
                    if type(value) not in (int, float) or not math.isfinite(value):
                        raise ValueError(f"YouTube Analytics returned a nonnumeric value for {name}")
                    if data_type == "INTEGER":
                        if int(value) != value:
                            raise ValueError(f"YouTube Analytics returned a fractional count for {name}")
                        record[name] = int(value)
                records.append({"channel_id": self.config["query_reports"]["channel_id"], **record})
        except (KeyError, TypeError, ValueError) as error:
            raise AirbyteTracedException(message=str(error), failure_type=FailureType.system_error) from error
        yield from records


@dataclass
class CustomDecoder(Decoder):
    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        fp = io.StringIO(response.text)
        reader = csv.DictReader(fp)
        for record in reader:
            yield record


@dataclass
class ContentOwnerRequester(HttpRequester):
    """
    Custom requester that conditionally adds the onBehalfOfContentOwner parameter
    only when content_owner_id is provided in the config.

    Also supports static `extra_request_parameters` declared in the manifest. `HttpRequester`
    has no such field, and the model factory only forwards manifest keys that match a
    component's type hints, so the field is declared here to be accepted and merged.

    Deliberately NOT named `request_parameters`: that key is already used by the `report`
    stream with a Jinja template value, and it is handled by the CDK's
    `InterpolatedRequestOptionsProvider` rather than by this class. Declaring a field of
    that name here makes the factory forward `report`'s template to this class, which
    merges values verbatim, sending the raw `{{ ... }}` text to the API as a query value.
    Values assigned to `extra_request_parameters` are NOT interpolated -- use static
    strings only.
    """

    extra_request_parameters: Optional[Mapping[str, Any]] = None

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().get_request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )
        if self.extra_request_parameters:
            params.update(self.extra_request_parameters)
        content_owner_id = self.config.get("content_owner_id")
        if content_owner_id:
            params["onBehalfOfContentOwner"] = content_owner_id
        return params


@dataclass
class JobRequester(ContentOwnerRequester):
    """
    Sends request to create a report job if it doesn't exist yet.
    Extends ContentOwnerRequester to conditionally add onBehalfOfContentOwner parameter.
    """

    JOB_NAME = "Airbyte reporting job"

    def send_request(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> Optional[requests.Response]:
        response = super().send_request(
            stream_state,
            stream_slice,
            next_page_token,
            path,
            request_headers,
            request_params,
            request_body_data,
            request_body_json,
            log_formatter,
        )

        # Later pages are only fetched by the paginator after the first page already made sure
        # the job exists.
        if next_page_token:
            return response

        if not self._job_exists(response, path, stream_state, stream_slice, request_headers, request_params, log_formatter):
            self._http_client.send_request(
                http_method="post",
                url=self._get_url(
                    path=path,
                    stream_state=stream_state,
                    stream_slice=stream_slice,
                    next_page_token=next_page_token,
                ),
                request_kwargs={"stream": self.stream_response},
                headers=self._request_headers(stream_state, stream_slice, next_page_token, request_headers),
                json={"name": self.JOB_NAME, "reportTypeId": self._parameters["report_type_id"]},
                dedupe_query_params=True,
                log_formatter=log_formatter,
                exit_on_rate_limit=self._exit_on_rate_limit,
            )
            response = super().send_request(
                stream_state,
                stream_slice,
                next_page_token,
                path,
                request_headers,
                request_params,
                request_body_data,
                request_body_json,
                log_formatter,
            )

        return response

    def _job_exists(
        self,
        response: requests.Response,
        path: Optional[str],
        stream_state: Optional[StreamState],
        stream_slice: Optional[StreamSlice],
        request_headers: Optional[Mapping[str, Any]],
        request_params: Optional[Mapping[str, Any]],
        log_formatter: Optional[Callable[[requests.Response], Any]],
    ) -> bool:
        """Whether a job for this stream's report type is on any page of `jobs.list`.

        The job can be on a later page than the first, and creating a second job for the same
        report type is wasted quota, so every page is checked before deciding to create one.
        """
        while True:
            response_json = self._parse_jobs_page(response)
            # The API returns {} instead of {"jobs": []} when no jobs exist yet.
            if any(job.get("reportTypeId") == self._parameters["report_type_id"] for job in response_json.get("jobs", [])):
                return True
            next_page = response_json.get("nextPageToken")
            if not next_page:
                return False
            response = super().send_request(
                stream_state,
                stream_slice,
                {"next_page_token": next_page},
                path,
                request_headers,
                {**(request_params or {}), "pageToken": next_page},
                None,
                None,
                log_formatter,
            )

    @staticmethod
    def _parse_jobs_page(response: requests.Response) -> Mapping[str, Any]:
        response_json = response.json()
        if "error" in response_json:
            error_details = response_json["error"]
            error_code = error_details.get("code", "unknown")
            api_message = error_details.get("message", str(error_details))
            error_message = f"YouTube Reporting API Error (code {error_code}): {api_message}. "
            raise AirbyteTracedException(message=error_message, failure_type=FailureType.config_error)
        return response_json


class ReportsStateMigration(StateMigration):
    """Rebuilds pre-1.1.0 (Python connector) state, ``{"date": 20251107}``, into the low-code shape.

    The child keeps its `date` cursor: it is a real column in the downloaded CSV and part of
    every child stream's primary key. The parent is seeded with the same value under the same
    key so that `ReportsCreateTimeStateMigration` can re-key it like any other legacy state.
    """

    _CURSOR_FIELD = "date"

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool(stream_state) and self._CURSOR_FIELD in stream_state and "state" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        cursor_value = str(stream_state[self._CURSOR_FIELD])
        return {
            "state": {self._CURSOR_FIELD: cursor_value},
            "parent_state": {"report": {"state": {self._CURSOR_FIELD: cursor_value}}},
        }


class ReportsCreateTimeStateMigration(StateMigration):
    """Re-keys the `report` parent cursor from `date` onto `createTime`.

    Two low-code saved-state shapes exist in the wild (pre-low-code state is rebuilt into the
    first by `ReportsStateMigration` beforehand):

    1. 1.1.0 through 1.3.4:
       ``{"state": {"date": "20251107"},
          "parent_state": {"report": {"state": {"date": "20251107"}, ...}}}``
       The parent's `date` holds a `%Y%m%d` data day copied off the child. The parent's declared
       cursor field did not exist on a report listing, so it never advanced on its own and many
       connections have no parent cursor at all.
    2. 1.3.5, if it reached any connection: as (1), but the parent's `date` holds a `createTime`
       timestamp under the old key name.

    Both convert to `parent_state.report.state.createTime`. The conversion can only move the
    cursor backwards: for any report file `createTime > endTime > startTime >= midnight of the
    data day`, so every legacy value is at or before the true `createTime`. A migrated connection
    re-lists at most a day or two of report files once, and can never skip one -- which is why
    re-keying the cursor is not a breaking change.

    The child streams' own `state.date` is deliberately left alone: it is a real column in the
    downloaded CSV and part of every child stream's primary key.
    """

    _LEGACY_CURSOR_FIELD = "date"
    _CURSOR_FIELD = "createTime"
    # `report.incremental_sync.datetime_format`.
    _CURSOR_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    _INPUT_FORMATS = ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y%m%d")

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if not stream_state or "state" not in stream_state:
            return False
        report_state = stream_state.get("parent_state", {}).get("report", {})
        if any(self._LEGACY_CURSOR_FIELD in cursor for cursor in self._cursor_dicts(report_state)):
            return True
        # Nothing to re-key, but the parent has no cursor of its own to carry forward either.
        # Seed it from the child so upgrading does not trigger a full re-read of everything
        # YouTube still retains.
        return not self._has_cursor(report_state) and bool(stream_state.get("state", {}).get(self._LEGACY_CURSOR_FIELD))

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        migrated = deepcopy(dict(stream_state))
        child_state = migrated.get("state")
        if isinstance(child_state, dict) and self._LEGACY_CURSOR_FIELD in child_state:
            child_state[self._LEGACY_CURSOR_FIELD] = str(child_state[self._LEGACY_CURSOR_FIELD])

        report_state = migrated.setdefault("parent_state", {}).setdefault("report", {})
        for cursor in self._cursor_dicts(report_state):
            legacy_value = cursor.pop(self._LEGACY_CURSOR_FIELD, None)
            converted = self._to_cursor_value(legacy_value) if legacy_value is not None else None
            if converted:
                cursor[self._CURSOR_FIELD] = converted

        if not self._has_cursor(report_state) and isinstance(child_state, dict) and child_state.get(self._LEGACY_CURSOR_FIELD):
            seed = self._to_cursor_value(child_state[self._LEGACY_CURSOR_FIELD])
            if seed:
                report_state["state"] = {self._CURSOR_FIELD: seed}
        if report_state.get("state") == {}:
            del report_state["state"]
        if not report_state:
            del migrated["parent_state"]["report"]
            if not migrated["parent_state"]:
                del migrated["parent_state"]
        return migrated

    @staticmethod
    def _cursor_dicts(report_state: Mapping[str, Any]) -> List[MutableMapping[str, Any]]:
        """Every dict in the parent's state that holds a cursor value.

        `ConcurrentPerPartitionCursor` keeps a global cursor under `state` and a per-partition
        one under each entry of `states`. Both have to be re-keyed, or the stream reads a mix of
        migrated and unmigrated partitions.
        """
        cursors = []
        if isinstance(report_state.get("state"), dict):
            cursors.append(report_state["state"])
        for partition_state in report_state.get("states") or []:
            if isinstance(partition_state.get("cursor"), dict):
                cursors.append(partition_state["cursor"])
        return cursors

    @classmethod
    def _has_cursor(cls, report_state: Mapping[str, Any]) -> bool:
        return any(cursor.get(cls._CURSOR_FIELD) for cursor in cls._cursor_dicts(report_state))

    @classmethod
    def _to_cursor_value(cls, value: Any) -> Optional[str]:
        """Normalise a legacy cursor value to the cursor's `datetime_format`.

        Returns None if it cannot be parsed, in which case the caller omits the cursor and the
        stream falls back to `start_datetime`: one wasteful full re-read, rather than a hard
        failure or an unparseable value reaching the cursor. `integration_tests/
        abnormal_state.json` carries `{"date": 99999999}`, which is exactly such a value.
        """
        text = str(value)
        for input_format in cls._INPUT_FORMATS:
            try:
                return datetime.strptime(text, input_format).strftime(cls._CURSOR_FORMAT)
            except ValueError:
                continue
        return None
