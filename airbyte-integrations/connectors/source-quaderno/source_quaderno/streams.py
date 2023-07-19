#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import math
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.sources.streams.http import HttpStream

DEFAULT_PRIMARY_KEY = "id"
DEFAULT_CURSOR = "id"
DEFAULT_SORT_KEY = "created_at"
DEFAULT_LIMIT = 100


class QuadernoStream(HttpStream):
    """
    This class represents a stream output by the connector.

    Each stream should extend this class to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/invoices
        - GET v1/credits

    then you should have three classes:
    `class QuadernoStream(HttpStream)` which is the current class
    `class Invoices(QuadernoStream)` contains behavior to pull data for invoices using invoices
    `class Credits(QuadernoStream)` contains behavior to pull data for employees using credits

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalQuadernoStream(QuadernoStream)`. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    path = None

    def __init__(self, config: dict, **kwargs):
        super().__init__(**kwargs)
        self._url_base = f"https://{config['account_name']}.quadernoapp.com/api/"
        self._start_date = None
        if config.get("start_date"):
            self._start_date = config["start_date"]

    @property
    def url_base(self) -> str:
        return self._url_base

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        The Quaderno resource primary key. Most of the Quaderno resources have `id` as a primary ID. Other Quaderno
        resources have different primary key or a composite key can override this method.

        :return: The Quaderno resource primary key(s)
        :rtype: Either `str`, list(str) or list(list(str))
        """
        return DEFAULT_PRIMARY_KEY

    @property
    def limit(self) -> int:
        """
        Returns the number of records limit
        """
        return DEFAULT_LIMIT

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """ Return a mapping (e.g: dict) containing information needed to query the next page in the response.
        :param response: the most recent response from the API
        :return If there is another page in the result, a dict containing information needed to query the next page.
                If there are no more pages in the result, return None.
        """
        if response.headers["x-pages-hasmore"] == "true":
            parsed_url = urlparse(response.headers["x-pages-nextpage"])
            return dict(parse_qsl(parsed_url.query))

        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """Define any query parameters to be set."""
        params = {"limit": 100}
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        response_json = response.json()
        yield from response_json


class IncrementalQuadernoStream(QuadernoStream):

    state_checkpoint_interval = 10

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Returns the cursor field to be used in the `incremental` sync mode.

        By default enable the `incremental` sync mode for all resources.

        :return: The cursor field(s) to be used in the `incremental` sync mode.
        :rtype: Union[str, List[str]]
        """
        return DEFAULT_CURSOR

    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """
        Determine the latest state after reading the latest record by comparing the cursor_field from the latest record
        and the current state and picks the 'most' recent cursor. This is how a stream's state is determined.
        Required for incremental.
        """
        current_id = (current_stream_state or {}).get(self.cursor_field, math.inf)
        latest_record_id = latest_record[self.cursor_field]

        return {self.cursor_field: min(current_id, latest_record_id)}


class Credits(IncrementalQuadernoStream):

    def path(self, **kwargs) -> str:
        return "credits"


class Contacts(IncrementalQuadernoStream):

    def path(self, **kwargs) -> str:
        return "contacts"


class Invoices(IncrementalQuadernoStream):

    def path(self, **kwargs) -> str:
        return "invoices"
