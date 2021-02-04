"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Generator

import backoff
import requests
from base_python import BaseClient
from requests.models import Response
from requests.status_codes import codes as status_codes

PAGE_SIZE = 50


class TooManyRequests(Exception):
    """Too many requests"""


class Client(BaseClient):
    BASE_URL = "https://api.sendgrid.com/v3/"

    def __init__(self, apikey: str):
        self._headers = {"Authorization": f"Bearer {apikey}"}
        super().__init__()

    def health_check(self):
        resp_data = requests.get(f"{self.BASE_URL}scopes", headers=self._headers)
        if resp_data.status_code == status_codes.OK:
            return True, None

        return False, resp_data.json()["errors"][0]["message"]

    @backoff.on_exception(backoff.expo, TooManyRequests, max_tries=6)
    def _request(self, url: str, **kwargs) -> Response:
        response = requests.get(url, headers=self._headers, **kwargs)
        if response.status_code == status_codes.TOO_MANY_REQUESTS:
            raise TooManyRequests()
        return response

    def _paginator(self, stream_url: str, pagination_type: str = None, key: str = None) -> Generator[dict, None, None]:
        if not pagination_type:
            response = self._request(f"{self.BASE_URL}{stream_url}")
            if response.status_code == status_codes.OK:
                yield from response.json()[key] if key else response.json()
            return
        elif pagination_type == "offset":
            offset = 0
            while True:
                response = self._request(f"{self.BASE_URL}{stream_url}?limit={PAGE_SIZE}&offset={offset}")
                if response.status_code != status_codes.OK:
                    return
                stream_data = response.json()[key] if key else response.json()
                yield from stream_data

                if len(stream_data) < PAGE_SIZE:
                    return
                offset += PAGE_SIZE
        elif pagination_type == "metadata":
            response = self._request(f"{self.BASE_URL}{stream_url}", params={"page_size": PAGE_SIZE})
            if response.status_code != status_codes.OK:
                return
            stream_data = (response.json()[key] if key else response.json()) or []
            yield from stream_data

            while response.json()["_metadata"].get("next", False):
                response = self._request(response.json()["_metadata"]["next"])
                if response.status_code != status_codes.OK:
                    return
                stream_data = (response.json()[key] if key else response.json()) or []
                yield from stream_data

    def stream__lists(self, fields):
        yield from self._paginator("marketing/lists", pagination_type="metadata", key="result")

    def stream__campaigns(self, fields):
        yield from self._paginator("marketing/campaigns", pagination_type="metadata", key="result")

    def stream__contacts(self, fields):
        yield from self._paginator("marketing/contacts", key="result")

    def stream__stats_automations(self, fields):
        yield from self._paginator("marketing/stats/automations", pagination_type="metadata", key="results")

    def stream__segments(self, fields):
        yield from self._paginator("marketing/segments", key="results")

    def stream__templates(self, fields):
        yield from self._paginator("templates?generations=legacy,dynamic", pagination_type="metadata", key="result")

    def stream__global_suppressions(self, fields):
        yield from self._paginator("suppression/unsubscribes", pagination_type="offset")

    def stream__suppression_groups(self, fields):
        yield from self._paginator("asm/groups")

    def stream__suppression_group_members(self, fields):
        yield from self._paginator("asm/suppressions", pagination_type="offset")

    def stream__blocks(self, fields):
        yield from self._paginator("suppression/blocks", pagination_type="offset")

    def stream__bounces(self, fields):
        yield from self._paginator("suppression/bounces")

    def stream__invalid_emails(self, fields):
        yield from self._paginator("suppression/invalid_emails", pagination_type="offset")

    def stream__spam_reports(self, fields):
        yield from self._paginator("suppression/spam_reports", pagination_type="offset")
