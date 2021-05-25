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


import math
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class PosthogStream(HttpStream, ABC):
    url_base = ""
    primary_key = ""

    def __init__(self, **kwargs):
       super().__init__(**kwargs)
       raise NotImplementedError

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
       raise NotImplementedError
       return {}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        params = {"key": "value"}
        raise NotImplementedError
        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        raise NotImplementedError
        yield from response_json

    @property
    @abstractmethod
    def data_field(self) -> str:
        """the responce entry that contains useful data"""
        raise NotImplementedError('drop or redefine')


class IncrementalPosthogStream(PosthogStream, ABC):
    state_checkpoint_interval = math.inf

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        raise NotImplementedError('define or drop')
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def request_params(self, stream_state=None, stream_slice: Mapping[str, Any] = None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        raise NotImplementedError
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        raise NotImplementedError
        yield from response_json


class Annotations(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, **kwargs) -> str:
        raise NotImplementedError
        return "dummy1"



class Cohorts(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, **kwargs) -> str:
        raise NotImplementedError
        return "dummy2"


class Elements(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        raise NotImplementedError
        return "dummy3"

class Events(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        raise NotImplementedError
        return "dummy3"

class FeatureFlags(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        raise NotImplementedError
        return "dummy3"

class Insights(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        raise NotImplementedError
        return "dummy3"

class InsightsPath(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        raise NotImplementedError
        return "dummy3"

class InsightsSessions(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        raise NotImplementedError
        return "dummy3"

class Persons(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        raise NotImplementedError
        return "dummy3"

class Sessions(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        raise NotImplementedError
        return "dummy3"

class SessionsRecording(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        raise NotImplementedError
        return "dummy3"

class Trends(IncrementalPosthogStream):
    cursor_field = ""

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        raise NotImplementedError
        return "dummy3"
