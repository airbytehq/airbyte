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

import logging
from abc import ABC
from datetime import time, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream

logging.basicConfig(level=logging.DEBUG)

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
        self._user_agent = user_agent
        self._access_token = None
        self._expires = None

    @property
    def path_param(self):
        return self.name[:-1]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "User-Agent": self._user_agent,
        }

        return headers

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        records = response.json().get(self.data_field) or []
        for record in records:
            yield record

    def get_access_token(self) -> str:
        # The refresh_token never expires and may be used many times to generate each access_token
        # Since the refresh_token does not expire, it is not included in get access_token response
        if self._access_token is not None and self._expires > pendulum.now():
            return self._access_token

        headers = {}
        if self._user_agent:
            headers["User-Agent"] = self._user_agent

        response = requests.post(
            url=GOOGLE_TOKEN_URI,
            headers=headers,
            data={
                "grant_type": "refresh_token",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
            },
        )

        if response.status_code != 200:
            logging.info(f"Unauthorized, because error = {response.json()}")

        data = response.json()
        self._access_token = data["access_token"]
        self._expires = pendulum.now() + timedelta(seconds=data["expires_in"])
        logging.info("Authorized, token expires = {}".format(self._expires))
        return self._access_token


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

        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        headers["Content-Type"] = "application/json"

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
