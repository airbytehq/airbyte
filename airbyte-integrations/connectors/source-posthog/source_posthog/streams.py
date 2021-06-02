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
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class PosthogStream(HttpStream, ABC):
    url_base = "https://app.posthog.com/api/"
    primary_key = "id"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        if resp_json.get("next"):
            next_query_string = urllib.parse.urlsplit(resp_json["next"]).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
            if params:
                return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json", "User-Agent": "posthog-python/1.4.0"}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get(self.data_field)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {}
        if next_page_token:
            params.update(next_page_token)
        return params

    @property
    @abstractmethod
    def data_field(self) -> str:
        """the responce entry that contains useful data"""


class IncrementalPosthogStream(PosthogStream, ABC):
    state_checkpoint_interval = math.inf
    reversed_pagination = {"is_completed": False, "latest_response_state": {}, "is_new_page_available": False, "upgrade_to": {}}

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        if self.reversed_pagination["is_completed"]:
            return {}
        if "next" in resp_json and resp_json["next"]:
            next_query_string = urllib.parse.urlsplit(resp_json["next"]).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
            if params:
                return params

    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> Union[Mapping[str, Any], Tuple[Any, Mapping[str, Any]]]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        current_stream_state = current_stream_state or {}
        current_state = current_stream_state.get(self.cursor_field)
        latest_state = latest_record.get(self.cursor_field)  # 810->809->808

        if current_state and latest_state <= current_state:
            # return Tuple with any first element and current state
            return (-1, self.reversed_pagination["upgrade_to"])
        if (
            self.reversed_pagination["latest_response_state"]
            and latest_state <= self.reversed_pagination["latest_response_state"][self.cursor_field]
            and self.reversed_pagination["is_completed"]
        ):
            return self.reversed_pagination["upgrade_to"]

        return current_stream_state  # dont upgrade state until complete!

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        data = response_json[self.data_field]
        if data:
            if not ("next" in response_json and response_json["next"]):
                self.reversed_pagination["is_completed"] = True
            latest_field_value = data[-1][self.cursor_field]
            if stream_state:
                if latest_field_value <= stream_state.get(self.cursor_field):
                    self.reversed_pagination["upgrade_to"] = stream_state
                    yield from []
                else:
                    self.reversed_pagination["latest_response_state"] = stream_state

            else:
                self.reversed_pagination["latest_response_state"] = {self.cursor_field: latest_field_value}
            if not self.reversed_pagination["upgrade_to"]:
                self.reversed_pagination["upgrade_to"] = {self.cursor_field: data[0][self.cursor_field]}

        yield from data


class Annotations(PosthogStream):
    """
    Could not use inremental here. No option to sort in request provided by API.
    There are 3 possible key fields id, created_at, updated_at.
    The last one is the most suitable
    But response is always sorted DESC on `id or created_at`.
    If the field was updated and `updated_at` was increased, it did not change its position in response.
    So if we have 2766-2891 ids, state saved on id=2870 and update 2869th record,
    we'll miss the update. So no logical way to use incremental, it will be like full_refresh.
    """

    data_field = "results"

    def path(self, **kwargs) -> str:
        return "annotation"


class Cohorts(IncrementalPosthogStream):
    """
    normal ASC sorting. But without filters like `since`
    So we need to query all anyway, but we may skip already written reords for incremental.
    """

    cursor_field = "id"
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "cohort"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        if "next" in resp_json and resp_json["next"]:
            next_query_string = urllib.parse.urlsplit(resp_json["next"]).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
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
        data = response_json.get(self.data_field)
        if data and stream_state:
            last_record_curfield = data[-1][self.cursor_field]
            last_stream_curfield = stream_state[self.cursor_field]
            if last_stream_curfield >= last_record_curfield:
                yield from []
            else:
                first_record_curfield = data[0][self.cursor_field]
                if first_record_curfield > last_stream_curfield:
                    yield from data
                else:
                    slice_ = [i for i in data if i[self.cursor_field] > last_stream_curfield]
                    yield from slice_

        else:
            yield from data


class Elements(PosthogStream):
    data_field = "elements"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "element/stats"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        elements = [i[self.data_field][0] for i in response_json]
        yield from elements

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This enpoint returns full stats list and have no pagination.
        """
        return None


class Events(IncrementalPosthogStream):
    """
    CAUTION! API supports inserting custom timestamp.
    That may break incremental since there is no way to sort in request params.
    """

    cursor_field = "timestamp"
    data_field = "results"

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
    data_field = "results"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "feature_flag"


class Insights(PosthogStream):
    """
    NO WAY TO SORT TO IMPLETEMENT INCREMENTAL! id, created_at, last_refresh
    are ordered in a random (!) way, no DESC no ASC
    """

    data_field = "results"

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
    data_field = "results"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "person"


class Trends(PosthogStream):
    data_field = "result"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "insight/trend"
