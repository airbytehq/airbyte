#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import csv
import io
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Generator, List, Mapping, MutableMapping, Optional, Union

import requests

from airbyte_cdk import AirbyteTracedException, Decoder, FailureType
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.types import StreamSlice, StreamState


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

        response_json = response.json()

        # Handle error responses from the API
        if "error" in response_json:
            error_details = response_json["error"]
            error_code = error_details.get("code", "unknown")
            api_message = error_details.get("message", str(error_details))
            error_message = f"YouTube Reporting API Error (code {error_code}): {api_message}. "
            raise AirbyteTracedException(message=error_message, failure_type=FailureType.config_error)

        # Handle the case where API returns {} instead of {"jobs": []}
        # This can happen when no jobs exist yet - treat as empty list
        jobs_list = response_json.get("jobs", [])
        stream_job = [r for r in jobs_list if r["reportTypeId"] == self._parameters["report_type_id"]]

        if not stream_job:
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


class ReportsStateMigration(StateMigration):
    """Re-keys the `report` parent cursor from `date` onto `createTime`.

    Three saved-state shapes exist in the wild:

    1. pre-1.1.0 (the Python connector):
       ``{"date": 20251107}``
    2. 1.1.0 through 1.3.4:
       ``{"state": {"date": "20251107"},
          "parent_state": {"report": {"state": {"date": "20251107"}, ...}}}``
       The parent's `date` holds a `%Y%m%d` data day this migration used to copy off the child.
       The parent's declared cursor field did not exist on a report listing, so it never
       advanced on its own and many connections have no parent cursor at all.
    3. 1.3.5, if it reached any connection: as (2), but the parent's `date` holds a `createTime`
       timestamp under the old key name.

    All three convert to `parent_state.report.state.createTime`. The conversion can only move
    the cursor backwards: for any report file `createTime > endTime > startTime >= midnight of
    the data day`, so every legacy value is at or before the true `createTime`. A migrated
    connection re-lists at most a day or two of report files once, and can never skip one --
    which is why re-keying the cursor is not a breaking change.

    The child streams' own `state.date` is deliberately left alone: it is a real column in the
    downloaded CSV and part of every child stream's primary key.
    """

    _LEGACY_CURSOR_FIELD = "date"
    _CURSOR_FIELD = "createTime"
    # `report.incremental_sync.datetime_format`.
    _CURSOR_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    _INPUT_FORMATS = ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y%m%d")

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if not stream_state:
            return False
        if self._is_pre_low_code(stream_state):
            return True
        report_state = stream_state.get("parent_state", {}).get("report", {})
        if any(self._LEGACY_CURSOR_FIELD in cursor for cursor in self._cursor_dicts(report_state)):
            return True
        # Nothing to re-key, but the parent has no cursor of its own to carry forward either.
        # Seed it from the child so upgrading does not trigger a full re-read of everything
        # YouTube still retains.
        return not self._has_cursor(report_state) and bool(stream_state.get("state", {}).get(self._LEGACY_CURSOR_FIELD))

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if self._is_pre_low_code(stream_state):
            child_cursor_value = str(stream_state[self._LEGACY_CURSOR_FIELD])
            migrated: MutableMapping[str, Any] = {"state": {self._LEGACY_CURSOR_FIELD: child_cursor_value}}
            seed = self._to_cursor_value(child_cursor_value)
            if seed:
                migrated["parent_state"] = {"report": {"state": {self._CURSOR_FIELD: seed}}}
            return migrated

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
        return migrated

    @classmethod
    def _is_pre_low_code(cls, stream_state: Mapping[str, Any]) -> bool:
        return cls._LEGACY_CURSOR_FIELD in stream_state and "state" not in stream_state

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
