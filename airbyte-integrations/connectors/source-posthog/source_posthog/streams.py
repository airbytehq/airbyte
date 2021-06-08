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
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class PosthogStream(HttpStream, ABC):
    url_base = "https://app.posthog.com/api/"
    primary_key = "id"
    data_field = "results"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        if resp_json.get("next"):
            next_query_string = urllib.parse.urlsplit(resp_json["next"]).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
            if params:
                return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json", "User-Agent": "posthog-python/1.4.0"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get(self.data_field, [])

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {}
        if next_page_token:
            params.update(next_page_token)
        return params


class IncrementalPosthogStream(PosthogStream, ABC):
    state_checkpoint_interval = math.inf

    def __init__(self, **kwargs):
        """
        Personal instance variables.
        @params _initial_state - contains initial state for each instance. Uses for interrupting next_page_token.
        @param _upgrade_to - first response state value.
            Example we have 5 pages of data from 500 to 1 with resp_size and state = 121.
            The loop will be interrupted after we got response containing [200-101] <- by _initial_state
            The value `500` will be a new state value we need to save it.
        """
        super().__init__(**kwargs)
        self._initial_state = None
        self._upgrade_state_to = None

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        data = response_json.get(self.data_field, [])
        if data:
            if self._initial_state and data[-1][self.cursor_field] <= self._initial_state:
                return {}
            params = super().next_page_token(response=response)
            if params:
                return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        if self._upgrade_state_to:
            return self._upgrade_state_to
        return current_stream_state

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        data = response_json.get(self.data_field, [])
        if data:
            if not self._upgrade_state_to:  # set once
                self._upgrade_state_to = {self.cursor_field: data[0][self.cursor_field]}
            if not stream_state:
                yield from data
            else:
                state_value = stream_state.get(self.cursor_field)
                if not self._initial_state:
                    self._initial_state = state_value
                for record in data:
                    record_cur_value = record.get(self.cursor_field)
                    if record_cur_value > state_value:
                        yield record
                    else:
                        break

        else:
            yield from data


class Annotations(IncrementalPosthogStream):
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "annotation"

    def request_params(self, stream_state: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:

        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["order"] = f"-{self.cursor_field}"
        return params


class Cohorts(IncrementalPosthogStream):
    """
    normal ASC sorting. But without filters like `since`
    """

    cursor_field = "id"

    def path(self, **kwargs) -> str:
        return "cohort"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        params = PosthogStream.next_page_token(self, response=response)
        if params:
            return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        current_stream_state = current_stream_state or {}
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        # need to skip response until data>stream_state
        data = response_json.get(self.data_field, [])
        if data and stream_state:
            state_value = stream_state.get(self.cursor_field)
            first_record_curvalue = data[0][self.cursor_field]
            if first_record_curvalue > state_value:  # skip page
                yield from []
            else:
                for record in data:
                    record_cur_value = record.get(self.cursor_field)
                    if record_cur_value <= state_value:
                        continue
                    else:
                        yield record

        else:
            yield from data


class Events(IncrementalPosthogStream):
    cursor_field = "timestamp"

    def __init__(self, start_date: str, **kwargs):
        self.start_date = start_date
        super().__init__(**kwargs)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "event"

    def request_params(self, stream_state=None, stream_slice: Mapping[str, Any] = None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        since_value = stream_state.get(self.cursor_field) or self.start_date
        since_value = max(since_value, self.start_date)
        if since_value:
            params["after"] = since_value
        return params


class EventsSessions(PosthogStream):
    data_field = "result"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "event/sessions"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        if "pagination" in resp_json and resp_json["pagination"]:
            return resp_json["pagination"]


class FeatureFlags(IncrementalPosthogStream):
    cursor_field = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "feature_flag"


class Insights(PosthogStream):
    """
    Endpoint does not support incremental read because id, created_at, last_refresh
    are ordered in a random way, no DESC no ASC
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "insight"


class InsightsPath(PosthogStream):
    data_field = "result"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "insight/path"


class InsightsSessions(PosthogStream):
    data_field = "result"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "insight/session"


class Persons(IncrementalPosthogStream):
    cursor_field = "created_at"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "person"


class Trends(PosthogStream):
    data_field = "result"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "insight/trend"
