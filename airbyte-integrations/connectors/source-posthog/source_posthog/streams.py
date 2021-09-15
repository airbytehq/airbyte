#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import math
import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Sequence

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class PosthogStream(HttpStream, ABC):
    primary_key = "id"
    data_field = "results"

    def __init__(self, base_url: str, **kwargs):
        super().__init__(**kwargs)
        self._url_base = f"{base_url}/api/"

    @property
    def url_base(self) -> str:
        return self._url_base

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        if resp_json.get("next"):
            next_query_string = urllib.parse.urlsplit(resp_json["next"]).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
            return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json", "User-Agent": "posthog-python/1.4.0"}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_data = response.json()
        if self.data_field:
            response_data = response_data.get(self.data_field)

        if isinstance(response_data, Sequence):
            yield from response_data
        elif response_data:
            yield response_data

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {}
        if next_page_token:
            params.update(next_page_token)
        return params


class IncrementalPosthogStream(PosthogStream, ABC):
    """
    Because endpoints has descending order we need to save initial state value to know when to stop pagination.
    start_date is used to as a min date to filter on.
    """

    state_checkpoint_interval = math.inf

    def __init__(self, base_url: str, start_date: str, **kwargs):
        super().__init__(base_url=base_url, **kwargs)
        self._start_date = start_date
        self._initial_state = None  # we need to keep it here because next_page_token doesn't accept state argument

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Return next page token until we reach the page with records older than state/start_date
        """
        response_json = response.json()
        data = response_json.get(self.data_field, [])
        latest_record = data[-1] if data else None  # records are ordered so we check only last one

        if not latest_record or latest_record[self.cursor_field] > self._initial_state:
            return super().next_page_token(response=response)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        Filter records by initial_state value
        """
        data = super().parse_response(response=response, stream_state=stream_state, **kwargs)
        for record in data:
            if record.get(self.cursor_field) >= self._initial_state:
                yield record

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Initialize initial_state value
        """
        stream_state = stream_state or {}
        self._initial_state = self._initial_state or stream_state.get(self.cursor_field) or self._start_date
        return super().read_records(sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state)


class Annotations(IncrementalPosthogStream):
    """
    Docs: https://posthog.com/docs/api/annotations
    """

    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "annotation"

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["order"] = f"-{self.cursor_field}"  # sort descending
        return params


class Cohorts(PosthogStream):
    """
    Docs: https://posthog.com/docs/api/cohorts
    normal ASC sorting. But without filters like `since`
    """

    def path(self, **kwargs) -> str:
        return "cohort"


class Events(IncrementalPosthogStream):
    """
    Docs: https://posthog.com/docs/api/events
    """

    cursor_field = "timestamp"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "event"

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        since_value = stream_state.get(self.cursor_field) or self._start_date
        since_value = max(since_value, self._start_date)
        params["after"] = since_value
        return params


class EventsSessions(PosthogStream):
    """
    Docs: https://posthog.com/docs/api/events
    """

    primary_key = "global_session_id"
    data_field = "result"

    def path(self, **kwargs) -> str:
        return "event/sessions"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        return resp_json.get("pagination")


class FeatureFlags(PosthogStream):
    """
    Docs: https://posthog.com/docs/api/feature-flags
    """

    def path(self, **kwargs) -> str:
        return "feature_flag"


class Insights(PosthogStream):
    """
    Docs: https://posthog.com/docs/api/insights
    Endpoint does not support incremental read because id, created_at and last_refresh are ordered in any particular way
    """

    def path(self, **kwargs) -> str:
        return "insight"


class InsightsPath(PosthogStream):
    """
    Docs: https://posthog.com/docs/api/insights
    """

    primary_key = None
    data_field = "result"

    def path(self, **kwargs) -> str:
        return "insight/path"


class InsightsSessions(PosthogStream):
    """
    Docs: https://posthog.com/docs/api/insights
    """

    primary_key = None
    data_field = "result"

    def path(self, **kwargs) -> str:
        return "insight/session"


class Persons(PosthogStream):
    """
    Docs: https://posthog.com/docs/api/people
    """

    def path(self, **kwargs) -> str:
        return "person"


class Trends(PosthogStream):
    """
    Docs: https://posthog.com/docs/api/insights
    """

    primary_key = None
    data_field = "result"

    def path(self, **kwargs) -> str:
        return "insight/trend"


class PingMe(PosthogStream):
    """
    Docs: https://posthog.com/docs/api/user
    """

    data_field = None

    def path(self, **kwargs) -> str:
        return "users/@me"
