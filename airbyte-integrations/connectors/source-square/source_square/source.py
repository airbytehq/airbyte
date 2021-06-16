#
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
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class SquareStream(HttpStream, ABC):
    def __init__(self, is_sandbox: bool, api_version: str, start_date: str, include_deleted_objects: bool, **kwargs):
        super().__init__(**kwargs)
        self.is_sandbox = is_sandbox
        self.api_version = api_version
        # Converting users ISO 8601 format (YYYY-MM-DD) to RFC 3339 (2021-06-14T13:47:56.799Z)
        # Because this standard is used by square in 'updated_at' records field
        self.start_date = "{}".format(pendulum.parse(start_date))
        self.include_deleted_objects = include_deleted_objects

    data_field = None
    primary_key = "id"

    @property
    def url_base(self) -> str:
        return "https://connect.squareup{}.com/v2/".format("sandbox" if self.is_sandbox else "")

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_cursor = response.json().get("cursor", False)
        if next_page_cursor:
            return {"cursor": next_page_cursor}

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Square-Version": self.api_version, "Content-Type": "application/json"}

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token if next_page_token else {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.data_field, []) if self.data_field is not None else json_response
        yield from records


class SquareCatalogObjectsStream(SquareStream):
    data_field = "objects"
    http_method = "POST"
    limit = 1000

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "catalog/search"

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping]:
        json_payload = {
            "include_deleted_objects": self.include_deleted_objects,
            "include_related_objects": False,
            "limit": self.limit
        }

        if next_page_token:
            json_payload.update({"cursor": next_page_token["cursor"]})

        return json_payload


class IncrementalSquareCatalogObjectsStream(SquareCatalogObjectsStream, ABC):
    state_checkpoint_interval = SquareCatalogObjectsStream.limit

    cursor_field = "updated_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
            Mapping[str, Any]:

        if current_stream_state is not None and self.cursor_field in current_stream_state:
            return {self.cursor_field: max(current_stream_state[self.cursor_field], latest_record[self.cursor_field])}
        else:
            return {self.cursor_field: self.start_date}

    def request_body_json(self, *args, **kwargs) -> Optional[Mapping]:
        return {
            **super(IncrementalSquareCatalogObjectsStream, self).request_body_json(*args, **kwargs),
            "begin_time": kwargs["stream_state"][self.cursor_field],
        }


class Items(IncrementalSquareCatalogObjectsStream):
    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return {**super(Items, self).request_body_json(**kwargs), "object_types": ["ITEM"]}


class Categories(IncrementalSquareCatalogObjectsStream):
    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return {**super(Categories, self).request_body_json(**kwargs), "object_types": ["CATEGORY"]}


class Discounts(IncrementalSquareCatalogObjectsStream):
    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return {**super(Discounts, self).request_body_json(**kwargs), "object_types": ["DISCOUNT"]}


class Taxes(IncrementalSquareCatalogObjectsStream):
    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return {**super(Taxes, self).request_body_json(**kwargs), "object_types": ["TAX"]}


class Locations(SquareStream):
    data_field = "locations"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "locations"


# Source
class SourceSquare(AbstractSource):
    api_version = "2021-05-13"  # Latest Stable Release

    def check_connection(self, logger, config) -> Tuple[bool, any]:

        headers = {
            "Square-Version": self.api_version,
            "Authorization": "Bearer {}".format(config["api_key"]),
            "Content-Type": "application/json",
        }
        url = "https://connect.squareup{}.com/v2/catalog/info".format("sandbox" if config["is_sandbox"] else "")

        try:
            session = requests.get(url, headers=headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = TokenAuthenticator(token=config["api_key"])
        args = {
            "authenticator": auth,
            "is_sandbox": config["is_sandbox"],
            "api_version": self.api_version,
            "start_date": config["start_date"],
            "include_deleted_objects": config['include_deleted_objects']
        }
        return [Items(**args), Categories(**args), Discounts(**args), Taxes(**args), Locations(**args)]
