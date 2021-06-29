# MIT License
#
# Copyright (c) 2021 Airbyte
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


from abc import ABC
import urllib.parse as urlparse
from urllib.parse import parse_qs
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import pendulum

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
import logging

#logging.basicConfig(level=logging.DEBUG)

# Basic full refresh stream
class TypeformStream(HttpStream, ABC):
    url_base = "https://api.typeform.com"

    limit: int = 2

    date_format: str = "YYYY-MM-DDTHH:mm:ss[Z]"

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        page = self.get_current_page_token(response.url)
        # if page field not found - finish pagination
        next_page = (
            None if page is None or response.json()["page_count"] <= page else page + 1
        )
        return next_page

    def get_current_page_token(self, url: str) -> Optional[int]:
        parsed = urlparse.urlparse(url)
        page = parse_qs(parsed.query).get("page")
        return int(page[0]) if page else None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"page_size": self.limit}
        if next_page_token:
            params["page"] = next_page_token
        else:
            params["page"] = 1

        return params

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        for item in response.json()["items"]:
            yield item


class Forms(TypeformStream):
    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "id"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "/forms"


# Basic incremental stream
class IncrementalTypeformStream(TypeformStream, ABC):
    cursor_field: str = "submitted_at"

    token_field: str = "token"

    @property
    def limit(self):
        return super().limit

    state_checkpoint_interval = limit

    min_cursor: str = "1970-01-01T00:00:00Z"

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        return {
            self.cursor_field: max(
                pendulum.from_format(
                    latest_record.get(self.cursor_field, self.min_cursor),
                    self.date_format,
                ),
                pendulum.from_format(
                    current_stream_state.get(self.cursor_field, self.min_cursor),
                    self.date_format,
                ),
            )
        }

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        items = response.json()["items"]
        breakpoint()
        if items and len(items) == self.limit:
            return items[-1][self.token_field]
        return None


class Responses(IncrementalTypeformStream):

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "response_id"

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"/forms/{stream_slice['form_id']}/responses"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        forms = Forms(authenticator=self.authenticator)
        for item in forms.read_records(sync_mode=SyncMode.full_refresh):
            yield {"form_id": item["id"]}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )
        stream_state = stream_state or {}
        if stream_state and not next_page_token:
            # use state for first request in incremental sync
            params["sort"] = "submitted_at,asc"
            params["since"] = stream_state.get(self.cursor_field)
        elif next_page_token:
            # use response token for pagination after first request
            params["after"] = next_page_token

        del params["page"]
        return params


class SourceTypeform(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            url = f"{TypeformStream.url_base}/forms"
            auth_headers = {"Authorization": f"Bearer {config['token']}"}
            session = requests.get(url, headers=auth_headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["token"])
        return [Forms(authenticator=auth), Responses(authenticator=auth)]
