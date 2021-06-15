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


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""

import logging

logging.basicConfig(level=logging.DEBUG)


class SquareStream(HttpStream, ABC):

    def __init__(self, is_sandbox: bool, api_version: str, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self.is_sandbox = is_sandbox
        self.api_version = api_version
        # Converting users ISO 8601 format (YYYY-MM-DD) to RFC 3339 (2021-06-14T13:47:56.799Z)
        # Because this standard is used in 'updated_at' records field
        self.start_date = '{}'.format(pendulum.parse(start_date))

    data_field = None
    primary_key = 'id'

    @property
    def url_base(self) -> str:
        return "https://connect.squareup{}.com/v2/".format('sandbox' if self.is_sandbox else '')

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_cursor = response.json().get("cursor", False)
        if next_page_cursor:
            return {"cursor": next_page_cursor}

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {'Square-Version': self.api_version, "Content-Type": "application/json"}

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
    """
    TODO remove this comment

    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class SquareStream(HttpStream, ABC)` which is the current class
    `class Customers(SquareStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(SquareStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalSquareStream((SquareStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    data_field = 'objects'
    http_method = 'POST'
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
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        json_payload = {
            "include_deleted_objects": True,
            "include_related_objects": False,
            "limit": self.limit
        }

        if next_page_token:
            json_payload.update({'cursor': next_page_token['cursor']})

        return json_payload


class IncrementalSquareCatalogObjectsStream(SquareCatalogObjectsStream, ABC):
    state_checkpoint_interval = SquareCatalogObjectsStream.limit

    cursor_field = "updated_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
            Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        if current_stream_state is not None and self.cursor_field in current_stream_state:
            return {self.cursor_field: max(current_stream_state[self.cursor_field], latest_record[self.cursor_field])}
        else:
            return {self.cursor_field: self.start_date}


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
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        headers = {
            "Square-Version": self.api_version,
            "Authorization": "Bearer {}".format(config["api_key"]),
            "Content-Type": "application/json"
        }
        url = "https://connect.squareup{}.com/v2/catalog/info".format('sandbox' if config['is_sandbox'] else '')

        try:
            session = requests.get(url, headers=headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as error:
            return False, error

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = TokenAuthenticator(token=config["api_key"])
        args = {'authenticator': auth,
                'is_sandbox': config['is_sandbox'],
                'api_version': self.api_version,
                'start_date': config['start_date']}
        return [
            Items(**args),
            Categories(**args),
            Discounts(**args),
            Taxes(**args),
            Locations(**args)
        ]
