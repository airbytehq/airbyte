#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import urllib.parse as urlparse
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib.parse import parse_qsl

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from requests.exceptions import HTTPError

from ..utils import safe_max

API_VERSION = 3


class JiraStream(HttpStream, ABC):
    """
    Jira API Reference: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
    """

    page_size = 50
    primary_key: Optional[str] = "id"
    extract_field: Optional[str] = None
    api_v1 = False
    skip_http_status_codes = []

    def __init__(self, domain: str, projects: List[str], **kwargs):
        super().__init__(**kwargs)
        self._domain = domain
        self._projects = projects

    @property
    def url_base(self) -> str:
        if self.api_v1:
            return f"https://{self._domain}/rest/agile/1.0/"
        return f"https://{self._domain}/rest/api/{API_VERSION}/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        if isinstance(response_json, dict):
            startAt = response_json.get("startAt")
            if startAt is not None:
                startAt += response_json["maxResults"]
                if "isLast" in response_json:
                    if response_json["isLast"]:
                        return
                elif "total" in response_json:
                    if startAt >= response_json["total"]:
                        return
                return {"startAt": startAt}
        elif isinstance(response_json, list):
            if len(response_json) == self.page_size:
                query_params = dict(parse_qsl(urlparse.urlparse(response.url).query))
                startAt = int(query_params.get("startAt", 0)) + self.page_size
                return {"startAt": startAt}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"maxResults": self.page_size}
        if next_page_token:
            params.update(next_page_token)
        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json if not self.extract_field else response_json.get(self.extract_field, [])
        if isinstance(records, list):
            for record in records:
                yield self.transform(record=record, **kwargs)
        else:
            yield self.transform(record=records, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return record

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(**kwargs)
        except HTTPError as e:
            if not (self.skip_http_status_codes and e.response.status_code in self.skip_http_status_codes):
                raise e


class StartDateJiraStream(JiraStream, ABC):
    def __init__(self, start_date: Optional[pendulum.DateTime] = None, **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date


class IncrementalJiraStream(StartDateJiraStream, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._starting_point_cache = {}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        updated_state = latest_record[self.cursor_field]
        stream_state_value = current_stream_state.get(self.cursor_field)
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        current_stream_state[self.cursor_field] = updated_state
        return current_stream_state

    def jql_compare_date(self, stream_state: Mapping[str, Any]) -> Optional[str]:
        compare_date = self.get_starting_point(stream_state)
        if compare_date:
            compare_date = compare_date.strftime("%Y/%m/%d %H:%M")
            return f"{self.cursor_field} >= '{compare_date}'"

    def get_starting_point(self, stream_state: Mapping[str, Any]) -> Optional[pendulum.DateTime]:
        if self.cursor_field not in self._starting_point_cache:
            self._starting_point_cache[self.cursor_field] = self._get_starting_point(stream_state=stream_state)
        return self._starting_point_cache[self.cursor_field]

    def _get_starting_point(self, stream_state: Mapping[str, Any]) -> Optional[pendulum.DateTime]:
        if stream_state:
            stream_state_value = stream_state.get(self.cursor_field)
            if stream_state_value:
                stream_state_value = pendulum.parse(stream_state_value)
                return safe_max(stream_state_value, self._start_date)
        return self._start_date

    def read_records(
        self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        start_point = self.get_starting_point(stream_state=stream_state)
        for record in super().read_records(stream_slice=stream_slice, stream_state=stream_state, **kwargs):
            cursor_value = pendulum.parse(record[self.cursor_field])
            if not start_point or cursor_value >= start_point:
                yield record

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        self._starting_point_cache.clear()
        yield from super().stream_slices(**kwargs)
