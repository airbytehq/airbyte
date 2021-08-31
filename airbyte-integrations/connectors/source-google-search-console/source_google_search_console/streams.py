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

import json
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import quote_plus, unquote_plus

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from airbyte_cdk.sources.streams.http.auth.oauth import Oauth2Authenticator
from source_google_search_console.service_account_authenticator import ServiceAccountAuthenticator

BASE_URL = "https://www.googleapis.com/webmasters/v3"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
ROW_LIMIT = 25000


class GoogleSearchConsole(HttpStream, ABC):
    url_base = BASE_URL
    primary_key = None
    data_field = None

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        site_urls: str,
        start_date: pendulum.datetime,
        service_account_info: str,
    ):
        super().__init__()
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._site_urls = self.get_urls_list(site_urls)
        self._start_date = start_date
        self._service_account_info = service_account_info

    @staticmethod
    def get_urls_list(site_urls: list) -> List[str]:
        return list(map(quote_plus, site_urls))

    @property
    def path_param(self):
        return self.name[:-1]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self._site_urls:
            return self._site_urls.pop(0)
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get(self.data_field) or []
        for record in records:
            yield record

    @property
    def authenticator(self) -> Union[HttpAuthenticator, None]:
        if self._client_id and self._client_secret and self._refresh_token:
            return Oauth2Authenticator(
                token_refresh_endpoint=GOOGLE_TOKEN_URI,
                client_secret=self._client_secret,
                client_id=self._client_id,
                refresh_token=self._refresh_token,
            )
        elif self._service_account_info:
            info = json.loads(self._service_account_info)
            return ServiceAccountAuthenticator(service_account_info=info)


class Sites(GoogleSearchConsole):
    """
    API docs: https://developers.google.com/webmaster-tools/search-console-api-original/v3/sites
    """

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"/sites/{next_page_token or self._site_urls.pop(0)}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()


class Sitemaps(GoogleSearchConsole):
    """
    API docs: https://developers.google.com/webmaster-tools/search-console-api-original/v3/sitemaps
    """

    data_field = "sitemap"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"/sites/{next_page_token or self._site_urls.pop(0)}/sitemaps"


class SearchAnalytics(GoogleSearchConsole, ABC):
    """
    API docs: https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics
    """

    data_field = "rows"
    start_row = 0
    value_field = None

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        site_urls: list,
        start_date: pendulum.datetime,
        service_account_info: str,
    ):
        super().__init__(client_id, client_secret, refresh_token, site_urls, start_date, service_account_info)
        self.search_types = ["web", "news", "image", "video"]

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"/sites/{self._site_urls[0]}/searchAnalytics/query"

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "date"

    @property
    def http_method(self) -> str:
        return "POST"

    def next_page_token(self, response: requests.Response) -> Optional[dict]:
        result = {}

        if len(response.json().get(self.data_field, [])) == ROW_LIMIT:
            self.start_row += ROW_LIMIT

        elif len(self.search_types) > 1:
            self.search_types.pop(0)
            self.start_row = 0

        elif len(self._site_urls) > 1:
            self._site_urls.pop(0)
            self.search_types = ["web", "news", "image", "video"]
            self.start_row = 0

        else:
            return None

        result["starRow"] = self.start_row
        result["searchType"] = self.search_types[0]

        return result

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        headers = {"Content-Type": "application/json"}
        return headers

    def request_body_json(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Dict[str, Any], str]]:

        start_date = self._start_date
        if start_date and stream_state:
            if stream_state.get(self.cursor_field):
                start_date = max(
                    pendulum.parse(stream_state[self.cursor_field]),
                    pendulum.parse(start_date),
                ).to_date_string()

        data = {
            "startDate": start_date,
            "endDate": stream_state.get("end_date") or pendulum.now().to_date_string(),
            "dimensions": ["date", self.value_field],
            "searchType": next_page_token.get("searchType") if isinstance(next_page_token, dict) else "web",
            "aggregationType": "auto",
            "startRow": next_page_token.get("starRow") if isinstance(next_page_token, dict) else 0,
            "rowLimit": ROW_LIMIT,
        }
        return data

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get(self.data_field) or []
        for record in sorted(records, key=lambda x: x["keys"][0]):
            record["site_url"] = unquote_plus(self._site_urls[0])
            record["date"] = record["keys"][0]
            record["searchType"] = self.search_types[0]
            record[self.value_field] = record.pop("keys")[1]
            yield record

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}


class SearchAnalyticsByCountry(SearchAnalytics):
    value_field = "country"


class SearchAnalyticsByDevice(SearchAnalytics):
    value_field = "device"


class SearchAnalyticsByPage(SearchAnalytics):
    value_field = "page"


class SearchAnalyticsByQuery(SearchAnalytics):
    value_field = "query"


class SearchAnalyticsByDate(SearchAnalytics):
    def request_body_json(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        data = super().request_body_json(stream_state, stream_slice, next_page_token)
        data["dimensions"] = ["date"]

        return data

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get(self.data_field) or []
        for record in records:
            record["site_url"] = unquote_plus(self._site_urls[0])
            record["searchType"] = self.search_types[0]
            record["date"] = record.pop("keys")[0]
            yield record


class SearchAnalyticsAllFields(SearchAnalytics):
    def request_body_json(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        data = super().request_body_json(stream_state, stream_slice, next_page_token)
        data["dimensions"] = ["date", "country", "device", "page", "query"]

        return data

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get(self.data_field) or []
        for record in records:
            record["site_url"] = unquote_plus(self._site_urls[0])
            record["searchType"] = self.search_types[0]
            record["date"] = record["keys"][0]
            record["country"] = record["keys"][1]
            record["device"] = record["keys"][2]
            record["page"] = record["keys"][3]
            record["query"] = record.pop("keys")[4]
            yield record
