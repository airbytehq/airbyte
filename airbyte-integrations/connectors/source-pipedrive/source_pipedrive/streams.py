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

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream

PIPEDRIVE_URL_BASE = "https://api.pipedrive.com/v1/"


class PipedriveStream(HttpStream, ABC):
    url_base = PIPEDRIVE_URL_BASE
    primary_key = "id"
    data_field = "data"

    def __init__(self, api_token: str, **kwargs):
        super().__init__(**kwargs)
        self._api_token = api_token

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        class_name = self.__class__.__name__
        return f"{class_name[0].lower()}{class_name[1:]}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"api_token": self._api_token}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        records = response.json().get(self.data_field) or []
        yield from records


class PaginatedPipedriveStream(PipedriveStream):
    limit = 50

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        pagination_data = response.json().get("additional_data", {}).get("pagination", {})
        if pagination_data.get("more_items_in_collection"):
            start = pagination_data.get("start", 0) + self.limit
            return {"start": start}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        next_page_token = next_page_token or {}
        params.update({"limit": self.limit, **next_page_token})
        return params


class IncrementalPipedriveStream(PaginatedPipedriveStream, ABC):
    cursor_field = "update_time"

    def __init__(self, replication_start_date: str = None, **kwargs):
        super().__init__(**kwargs)
        self._replication_start_date = replication_start_date

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

    @property
    @abstractmethod
    def path_param(self):
        pass

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        replication_start_date = stream_state.get(self.cursor_field) or self._replication_start_date
        params.update(
            {
                "items": self.path_param,
                "since_timestamp": replication_start_date,
            }
        )
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        records = super().parse_response(response=response, **kwargs)
        for record in records:
            yield record.get(self.data_field)

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "recents"


class Deals(IncrementalPipedriveStream):
    path_param = "deal"


class Leads(PaginatedPipedriveStream):
    pass


class Activities(IncrementalPipedriveStream):
    path_param = "activity"


class ActivityFields(PipedriveStream):
    pass


class Persons(IncrementalPipedriveStream):
    path_param = "activity"


class Pipelines(IncrementalPipedriveStream):
    path_param = "pipeline"


class Stages(IncrementalPipedriveStream):
    path_param = "stage"


class Users(IncrementalPipedriveStream):
    path_param = "user"
