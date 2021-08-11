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

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from airbyte_cdk.sources.streams.http.auth.oauth import Oauth2Authenticator

BASE_URL = "https://www.googleapis.com/webmasters/v3"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"


class GoogleSearchConsole(HttpStream, ABC):
    url_base = BASE_URL
    primary_key = "id"
    data_field = None

    def __init__(
        self, client_id: str, client_secret: str, refresh_token: str, site_urls: str, start_date: pendulum.datetime, user_agent=None
    ):
        super().__init__()
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._site_url = site_urls
        self._start_date = start_date

    @property
    def path_param(self):
        return self.name[:-1]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get(self.data_field) or []
        for record in records:
            yield record

    @property
    def authenticator(self) -> HttpAuthenticator:
        return Oauth2Authenticator(
            token_refresh_endpoint=GOOGLE_TOKEN_URI,
            client_secret=self._client_secret,
            client_id=self._client_id,
            refresh_token=self._refresh_token,
        )


class Sites(GoogleSearchConsole):
    """
    API docs: https://developers.google.com/webmaster-tools/search-console-api-original/v3/sites
    """

    def path(self, **kwargs) -> str:
        return f"/sites/{self._site_url}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()


class Sitemaps(GoogleSearchConsole):
    """
    API docs: https://developers.google.com/webmaster-tools/search-console-api-original/v3/sitemaps
    """

    data_field = "sitemap"

    def path(self, **kwargs) -> str:
        return f"/sites/{self._site_url}/sitemaps"


class SearchAnalytics(GoogleSearchConsole):
    """
    API docs: https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics
    """

    data_field = "row"

    def path(self, **kwargs) -> str:
        return f"/sites/{self._site_url}/searchAnalytics/query"

    @property
    def http_method(self) -> str:
        return "POST"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        headers = {"Content-Type": "application/json"}
        return headers

    def request_body_json(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Union[Mapping, str]]:
        data = {
            "startDate": str(self._start_date),
            "endDate": pendulum.now().to_date_string(),
            "dimensions": ["country", "device", "page", "query"],
            "searchType": "web",
            "aggregationType": "auto",
            "rowLimit": 25000,
        }

        return data
