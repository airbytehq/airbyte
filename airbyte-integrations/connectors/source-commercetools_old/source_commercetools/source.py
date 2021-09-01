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
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from urllib.parse import urlparse
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class CommercetoolsStream(HttpStream, ABC):

    # Page size
    limit = 500
    # Define primary key as sort key for full_refresh, or very first sync for incremental_refresh
    primary_key = "id"
    filter_field = "lastModifiedAt"
    offset = 0

    def __init__(self, region: str, project_key: str, start_date: str, access_token: str, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.project_key = project_key
        self.region = region
        self.access_token = access_token

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json()
        total = json_response.get("total", None)
        offset = json_response.get("offset", None)
        if offset+limit < total:
            return dict(offset=offset+self+limit)
        else:
            return None

    @property
    def url_base(self) -> str:
        return f"https://api.{self.region}.commercetools.com/"

    def path(self, **kwargs) -> str:
        return f"{self.data_field}"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"offset": self.offset}
        if next_page_token:
            params.update(**next_page_token)
        else:
            params.update({"sort":"lastModifiedAt asc"})
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get("results", []) if self.data_field is not None else json_response
        yield from records


# Basic incremental stream
class IncrementalCommercetoolsStream(CommercetoolsStream, ABC):

    @property
    def limit(self):
        return super().limit

    # Setting the default cursor field for all streams
    cursor_field = "lastModifiedAt"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        # If there is a next page token then we should only send pagination-related parameters.
        if not next_page_token:
            params["limit"] = self.limit
            params["sort"] = "lastModifiedAt asc"
            if stream_state:
                params["where"] = urlparse("lastModifiedAt >= :date")
                params["var.date"] = stream_state.get(self.cursor_field)
        return params

    # Parse the stream_slice with respect to stream_state for Incremental refresh
    # cases where we slice the stream, the endpoints for those classes don't accept any other filtering,
    # but they provide us with the updated_at field in most cases, so we used that as incremental filtering during the order slicing.
    def filter_records_newer_than_state(self, stream_state: Mapping[str, Any] = None, records_slice: Mapping[str, Any] = None) -> Iterable:
        # Getting records >= state
       if stream_state:
           for record in records_slice:
               if record[self.cursor_field] >= stream_state.get(self.cursor_field):
                   yield record
       else:
           yield from records_slice


class Customers(CommercetoolsStream):

    data_field = "customers"


class DiscountCodes(IncrementalCommercetoolsStream):

    data_field = "discount_codes"


class Orders(IncrementalCommercetoolsStream):

    data_field = "orders"


class Payments(IncrementalCommercetoolsStream):

    data_field = "payments"


class Products(IncrementalCommercetoolsStream):

    data_field = "products"


# Source
class SourceCommercetools(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = TokenAuthenticator(token=config["access_token"]).get_auth_header()
        url = f"https://api.{config["region"]}.commercetools.com/{config["project_key"]}"
        try:
            session = requests.get(url, headers=auth)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["access_token"])
        args = {"authenticator": auth, "region": config["region"], "project_key": config["project_key"], "start_date": config["start_date"], "access_token": config["access_token"]}

        return [
                    Customers(**args),
                    Orders(**args),
                    DiscountCodes(**args),
                    Payments(**args),
                    Products(**args)
                ]
