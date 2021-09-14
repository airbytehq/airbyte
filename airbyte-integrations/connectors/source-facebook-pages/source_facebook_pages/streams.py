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

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from source_facebook_pages.metrics import PAGE_FIELDS, PAGE_METRICS, POST_FIELDS, POST_METRICS


class FacebookPagesStream(HttpStream, ABC):
    url_base = "https://graph.facebook.com/v11.0/"
    primary_key = "id"
    data_field = "data"

    def __init__(
        self,
        access_token: str = None,
        page_id: str = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._access_token = access_token
        self._page_id = page_id

    @property
    def path_param(self):
        return self.name[:-1]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()

        if not data.get("data") or not data.get("paging"):
            return {}

        return {
            "limit": 100,
            "after": data.get("paging", {}).get("cursors", {}).get("after"),
        }

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        next_page_token = next_page_token or {}
        params = {"access_token": self._access_token, **next_page_token}

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if not self.data_field:
            yield response.json()

        records = response.json().get(self.data_field, [])

        for record in records:
            yield record


class Page(FacebookPagesStream):
    """
    API docs: https://developers.facebook.com/docs/graph-api/reference/page/,
    """

    data_field = ""

    def path(self, **kwargs) -> str:
        return self._page_id

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        # we have to define which fields will return from Facebook API
        # because FB API doesn't provide opportunity to get fields dynamically without delays
        # so in PAGE_FIELDS we define fields that user can get from API
        params["fields"] = PAGE_FIELDS

        return params


class Post(FacebookPagesStream):
    """
    https://developers.facebook.com/docs/graph-api/reference/v11.0/page/feed,
    """

    def path(self, **kwargs) -> str:
        return f"{self._page_id}/posts"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["fields"] = POST_FIELDS

        return params


class PageInsights(FacebookPagesStream):
    """
    API docs: https://developers.facebook.com/docs/graph-api/reference/page/insights/,
    """

    def path(self, **kwargs) -> str:
        return f"{self._page_id}/insights"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["metric"] = ",".join(PAGE_METRICS)

        return params


class PostInsights(FacebookPagesStream):
    """
    API docs: https://developers.facebook.com/docs/graph-api/reference/post/insights/,
    """

    def path(self, **kwargs) -> str:
        return f"{self._page_id}/posts"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["fields"] = f'insights.metric({",".join(POST_METRICS)})'

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # unique case so we override this method
        records = response.json().get(self.data_field) or []

        for insights in records:
            if insights.get("insights"):
                data = insights.get("insights").get("data")
                for insight in data:
                    yield insight
            else:
                yield insights
