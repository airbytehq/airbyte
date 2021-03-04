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

from enum import Enum
from typing import Generator

import backoff
import requests
from base_python import BaseClient
from base_python.entrypoint import logger
from requests.models import Response
from requests.status_codes import codes as status_codes

PAGE_SIZE = 50


class Pagination(Enum):
    Non_pagination = 0
    Offset = 1
    Metadata = 2


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
            msg = f"Rate limit error: {response.json()}"
            logger.error(msg)
            raise TooManyRequests(msg)
        elif response.status_code != status_codes.OK:
            raise Exception(f"Unable to get data, error during request from url: {url}. Error: {response.json()}")
        return response

    def _read_data(self, stream_url: str, pagination: Pagination, key: str = None) -> Generator[dict, None, None]:
        if pagination == Pagination.Non_pagination:
            response = self._request(f"{self.BASE_URL}{stream_url}")
            yield from response.json()[key] if key else response.json()
        elif pagination == Pagination.Offset:
            offset = 0
            while True:
                response = self._request(f"{self.BASE_URL}{stream_url}?limit={PAGE_SIZE}&offset={offset}")
                stream_data = response.json()[key] if key else response.json()
                yield from stream_data

                if len(stream_data) < PAGE_SIZE:
                    return
                offset += PAGE_SIZE
        elif pagination == Pagination.Metadata:
            next_page_url, params = f"{self.BASE_URL}{stream_url}", {"page_size": PAGE_SIZE}
            while next_page_url:
                response = self._request(next_page_url, params=params)
                next_page_url, params = response.json()["_metadata"].get("next", False), {}

                # We use the "or []" construction to prevent the script from breaking in one single case:
                # for the "stats_automations" stream, if there are no records in the response, than "None" arrives,
                # in all other streams we get an empty list if there are no records.
                stream_data = (response.json()[key] if key else response.json()) or []
                yield from stream_data
        else:
            raise Exception(f"Unknown pagination type '{pagination.name}'")

    def stream__lists(self, fields):
        yield from self._read_data("marketing/lists", pagination=Pagination.Metadata, key="result")

    def stream__campaigns(self, fields):
        yield from self._read_data("marketing/campaigns", pagination=Pagination.Metadata, key="result")

    def stream__contacts(self, fields):
        yield from self._read_data("marketing/contacts", pagination=Pagination.Non_pagination, key="result")

    def stream__stats_automations(self, fields):
        yield from self._read_data("marketing/stats/automations", pagination=Pagination.Metadata, key="results")

    def stream__segments(self, fields):
        yield from self._read_data("marketing/segments", pagination=Pagination.Non_pagination, key="results")

    def stream__templates(self, fields):
        yield from self._read_data("templates?generations=legacy,dynamic", pagination=Pagination.Metadata, key="result")

    def stream__global_suppressions(self, fields):
        yield from self._read_data("suppression/unsubscribes", pagination=Pagination.Offset)

    def stream__suppression_groups(self, fields):
        yield from self._read_data("asm/groups", pagination=Pagination.Non_pagination)

    def stream__suppression_group_members(self, fields):
        yield from self._read_data("asm/suppressions", pagination=Pagination.Offset)

    def stream__blocks(self, fields):
        yield from self._read_data("suppression/blocks", pagination=Pagination.Offset)

    def stream__bounces(self, fields):
        yield from self._read_data("suppression/bounces", pagination=Pagination.Non_pagination)

    def stream__invalid_emails(self, fields):
        yield from self._read_data("suppression/invalid_emails", pagination=Pagination.Offset)

    def stream__spam_reports(self, fields):
        yield from self._read_data("suppression/spam_reports", pagination=Pagination.Offset)
