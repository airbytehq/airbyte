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


class SendgridStream(HttpStream, ABC):
    url_base = "https://api.sendgrid.com/v3/"
    primary_key = "id"
    limit = 50

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.data_field, []) if self.data_field is not None else json_response
        for record in records:
            yield record

    @property
    @abstractmethod
    def data_field(self) -> str:
        """The name of the field in the response which contains the data"""


class SendgridStreamOffsetPagination(SendgridStream):
    offset = 0

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.limit}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()[self.data_field] if self.data_field else response.json()
        if len(stream_data) < self.limit:
            return
        self.offset += self.limit
        return {"offset": self.offset}


class SendgridStreamMetadataPagination(SendgridStream):
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {}
        if not next_page_token:
            params = {"page_size": self.limit}
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_url = response.json()["_metadata"].get("next", False)
        if next_page_url:
            return {"next_page_url": next_page_url}

    @staticmethod
    @abstractmethod
    def initial_path() -> str:
        """
        :return: initial path for the API endpoint if no next metadata url found
        """

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        if next_page_token:
            return next_page_token["next_page_url"]
        return self.initial_path()

    def _create_prepared_request(
        self, path: str, headers: Mapping = None, params: Mapping = None, json: Any = None
    ) -> requests.PreparedRequest:
        url = self.url_base + path if self.url_base not in path else path
        args = {"method": self.http_method, "url": url, "headers": headers, "params": params}

        if self.http_method.upper() == "POST":
            args["json"] = json

        return requests.Request(**args).prepare()


class Scopes(SendgridStream):
    data_field = None

    def path(self, **kwargs) -> str:
        return "scopes"


class Lists(SendgridStreamMetadataPagination):
    data_field = "result"

    @staticmethod
    def initial_path() -> str:
        return "marketing/lists"


class Campaigns(SendgridStreamMetadataPagination):
    data_field = "result"

    @staticmethod
    def initial_path() -> str:
        return "marketing/campaigns"


class Contacts(SendgridStream):
    data_field = "result"

    def path(self, **kwargs) -> str:
        return "marketing/contacts"


class StatsAutomations(SendgridStreamMetadataPagination):
    data_field = "result"

    @staticmethod
    def initial_path() -> str:
        return "marketing/stats/automations"


class Segments(SendgridStream):
    data_field = "result"

    def path(self, **kwargs) -> str:
        return "marketing/segments"


class Templates(SendgridStreamMetadataPagination):
    data_field = "result"

    @staticmethod
    def initial_path() -> str:
        return "templates?generations=legacy,dynamic"


class GlobalSuppressions(SendgridStreamOffsetPagination):
    data_field = None

    def path(self, **kwargs) -> str:
        return "suppression/unsubscribes"


class SuppressionGroups(SendgridStream):
    data_field = None

    def path(self, **kwargs) -> str:
        return "asm/groups"


class SuppressionGroupMembers(SendgridStreamOffsetPagination):
    data_field = None

    def path(self, **kwargs) -> str:
        return "asm/suppressions"


class Blocks(SendgridStreamOffsetPagination):
    data_field = None

    def path(self, **kwargs) -> str:
        return "suppression/blocks"


class Bounces(SendgridStream):
    data_field = None

    def path(self, **kwargs) -> str:
        return "suppression/bounces"


class InvalidEmails(SendgridStreamOffsetPagination):
    data_field = None

    def path(self, **kwargs) -> str:
        return "suppression/invalid_emails"


class SpamReports(SendgridStreamOffsetPagination):
    data_field = None

    def path(self, **kwargs) -> str:
        return "suppression/spam_reports"
