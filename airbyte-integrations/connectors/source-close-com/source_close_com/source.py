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
from base64 import b64encode
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class CloseComStream(HttpStream, ABC):
    url_base: str = "https://api.close.com/api/v1/"
    primary_key: str = "id"
    limit: int = 100

    def __init__(self, **kwargs: Mapping[str, Any]):
        super().__init__(authenticator=kwargs["authenticator"])
        self.config: Mapping[str, Any] = kwargs

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if bool(decoded_response.get("has_more", None)) and decoded_response.get("data", []):
            parsed = dict(parse_qsl(urlparse(response.url).query))
            # close.com has default skip param - 0
            skip = parsed.get("_skip", 0)
            limit = parsed.get("_limit", self.limit)
            return {"_skip": int(skip) + int(limit)}
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        params = {"_limit": self.limit}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["data"]


class IncrementalCloseComStream(CloseComStream, ABC):
    last_date_updated: str = "2000-01-01"

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        return {
            self.cursor_field: max(
                latest_record.get(self.cursor_field) or self.last_date_updated,
                current_stream_state.get(self.cursor_field) or self.last_date_updated,
            )
        }


class Activities(IncrementalCloseComStream):
    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "activity"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["date_created__gt"] = stream_state.get(self.cursor_field)
        return params


class Events(IncrementalCloseComStream):
    cursor_field = "date_updated"
    limit = 50

    def path(self, **kwargs) -> str:
        return "event"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["date_updated__gt"] = stream_state.get(self.cursor_field)
        return params


class Leads(IncrementalCloseComStream):
    cursor_field = "date_updated"

    def path(self, **kwargs) -> str:
        return "lead"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["query"] = f"date_updated > {stream_state.get(self.cursor_field)}"
        return params


class Tasks(IncrementalCloseComStream):
    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "task"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["date_created__gt"] = stream_state.get(self.cursor_field)
        return params


class LeadCustomFields(CloseComStream):
    def path(self, **kwargs) -> str:
        return "custom_field/lead"


class ContactCustomFields(CloseComStream):
    def path(self, **kwargs) -> str:
        return "custom_field/contact"


class OpportunityCustomFields(CloseComStream):
    def path(self, **kwargs) -> str:
        return "custom_field/opportunity"


class ActivityCustomFields(CloseComStream):
    def path(self, **kwargs) -> str:
        return "custom_field/activity"


class Users(CloseComStream):
    def path(self, **kwargs) -> str:
        return "user"


class SourceCloseCom(AbstractSource):
    @staticmethod
    def _convert_auth_to_token(username: str, password: str) -> str:
        username = username.encode("latin1")
        password = password.encode("latin1")
        token = b64encode(b":".join((username, password))).strip().decode("ascii")
        return token

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            url = "https://api.close.com/api/v1/me"
            response = requests.request(
                "GET",
                url=url,
                auth=(config["api_key"], ""),
            )
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(auth_method="Basic", token=self._convert_auth_to_token(config["api_key"], ""))
        args = {"authenticator": authenticator}
        return [
            Activities(**args),
            Leads(**args),
            Tasks(**args),
            Events(**args),
            LeadCustomFields(**args),
            ContactCustomFields(**args),
            OpportunityCustomFields(**args),
            ActivityCustomFields(**args),
            Users(**args),
        ]
