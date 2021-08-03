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

from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from source_facebook_pages.metrics import PAGE_METRICS, POST_METRICS


class FacebookStream(HttpStream, ABC):
    url_base = "https://graph.facebook.com/v11.0/"
    primary_key = "id"
    data_field = "data"

    def __init__(
        self,
        access_token: str = None,
        page_id: str = None,
        start_date: pendulum.datetime = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._access_token = access_token
        self._start_date = start_date
        self._page_id = page_id
        self._query_field_param = []

    @property
    def path_param(self):
        return self.name[:-1]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        next_page_token = next_page_token or {}
        params = {"access_token": self._access_token, **next_page_token}

        return params

    def get_params(self, request_url):
        """
        Return all fields which correspond granted user permissions.
        We use this because we have to define which fields are returns from Facebook API
        """
        url = self.url_base + request_url
        params = {"access_token": self._access_token}

        for field in self._get_query_field_params(url):
            params["fields"] = field
            response = requests.get(url, params=params)
            if response.status_code == 200:
                self._query_field_param.append(field)

        params["fields"] = ",".join(self._get_query_field_params(url))
        return params

    def _get_query_field_params(self, url):
        if self._query_field_param:
            fields = self._query_field_param
        else:
            fields = self.get_all_fields(url)

        return fields

    def get_all_fields(self, url):
        """
        Return all available fields for some stream.
        We use this because we have to define which fields are returns from Facebook API
        """
        response = requests.get(url, params={"metadata": 1, "access_token": self._access_token})

        if response.status_code != 200:
            return []

        data = response.json()
        result = self._parse_fields(data)

        return result

    @staticmethod
    def _parse_fields(data):
        result = []
        try:
            connections = data["metadata"]["connections"]
            temp_fields = data["metadata"]["fields"]

            for field in temp_fields:
                result.append(field["name"])
            for conn_name in connections.keys():
                result.append(conn_name)

            if "access_token" in result:
                result.remove("access_token")

            return result

        except Exception:
            # fixme
            return []


class Page(FacebookStream):
    """
    API docs: https://developers.facebook.com/docs/graph-api/reference/page/,
    """

    def path(self, **kwargs) -> str:
        if self._page_id:
            return self._page_id

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = self.get_params(request_url=self._page_id)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()


class Post(FacebookStream):
    """
    API docs: https://developers.facebook.com/docs/graph-api/reference/post/,
    """

    def path(self, **kwargs) -> str:
        if self._page_id:
            return f"{self._page_id}/posts"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get(self.data_field) or []
        for record in records:
            yield record

    def get_post_url(self):
        response = requests.get(
            url=f"{self.url_base}/{self.path()}",
            params={"access_token": self._access_token},
        )
        try:
            # Take the first post url so we can extract metadata from it
            first_post = response.json().get("data")[0]
            url_first_post = first_post.get("id")
            return url_first_post

        except Exception:
            raise AttributeError

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        try:
            post_url = self.get_post_url()
            params = self.get_params(request_url=post_url)
        except AttributeError:
            params = super().request_params(stream_state, stream_slice, next_page_token)

        return params


class PageInsights(FacebookStream):
    """
    API docs: https://developers.facebook.com/docs/graph-api/reference/page/insights/,
    """

    def path(self, **kwargs) -> str:
        if self._page_id:
            return f'{self._page_id}/?fields=insights.metric({",".join(PAGE_METRICS)})'

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {"access_token": self._access_token}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("insights")
        records = data.get(self.data_field) or []

        for record in records:
            yield record


class PostInsights(FacebookStream):
    """
    API docs: https://developers.facebook.com/docs/graph-api/reference/post/insights/,
    """

    def path(self, **kwargs) -> str:
        if self._page_id:
            return f'{self._page_id}/posts/?fields=insights.metric({",".join(POST_METRICS)})'

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {"access_token": self._access_token}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get(self.data_field) or []

        for insights in records:
            if insights.get("insights"):
                data = insights.get("insights").get("data")
                for insight in data:
                    yield insight
            else:
                yield insights
