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
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import json
import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream


class FacebookStream(HttpStream, ABC):
    url_base = 'https://graph.facebook.com/'
    primary_key = "id"

    def __init__(self, access_token: str, page_id: str, start_date: pendulum.datetime = None, **kwargs):
        super().__init__(**kwargs)
        self._access_token = access_token
        self._start_date = start_date
        self._page_id = page_id

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        if self._start_date:
            return "update_time"
        return []

    @property
    def path_param(self):
        return self.name[:-1]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        next_page_token = next_page_token or {}
        params = {"access_token": self._access_token, **next_page_token}

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        records = response.json() or []
        yield records

    def get_page_token(self) -> Optional[str]:
        params = {
            'fields': 'access_token',
            'access_token': self._access_token
        }
        response = requests.get(url=f'https://graph.facebook.com/{self._page_id}', params=params)
        if response.status_code == 200:
            return json.loads(response.text)['access_token']
        else:
            return None


class Page(FacebookStream):
    """
    API docs: https://developers.facebook.com/docs/graph-api/reference/page/,
    """

    def path(self, **kwargs) -> str:
        if self._page_id:
            return self._page_id


class Post(FacebookStream):
    """
    API docs: https://developers.facebook.com/docs/graph-api/reference/post/,
    """

    def path(self, **kwargs) -> str:
        if self._page_id:
            return f'{self._page_id}/posts'


class PageInsights(FacebookStream):
    """
    API docs: https://developers.facebook.com/docs/graph-api/reference/page/insights/,
    """

    def path(self, **kwargs) -> str:
        if self._page_id:  # pass these metrics for now, fixme
            return f'{self._page_id}/?fields=insights.metric(' \
                   f'page_tab_views_login_top_unique,' \
                   f'page_tab_views_login_top,' \
                   f'page_tab_views_logout_top)'

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"access_token": self.get_page_token()}
