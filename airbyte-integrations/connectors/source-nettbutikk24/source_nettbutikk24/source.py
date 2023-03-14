#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pendulum
import requests
from abc import ABC
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple


def convert_date_to_epoch(date: str):
    return int(pendulum.parse(date).timestamp())


class Nettbutikk24Stream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.
    """

    # url_base = "https://brewshop.no/api/v1/"

    def __init__(self, config: Mapping[str, Any], flat: bool = False, **kwargs):
        super().__init__()
        self.access_token = config.get("access_token")
        self.shop_name = config.get("shop_name")
        self.flat = flat

        self.uri_params = {
            "since": convert_date_to_epoch(config.get('initial_start_date')),
            "offset": 0,
            "limit": 100,
        }

    @property
    def url_base(self):
        return f"http://{self.shop_name}/api/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        paging = response.json().get("paging", {})
        if type(paging) == list:
            return None

        next_path = paging.get("next")
        if next_path:
            offset = next_path.split("/")[7]
            return {"offset": offset}

        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"access_token": self.access_token, "flat": self.flat}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        if response.status_code == 404:
            yield from []

        yield from response.json().get("data", [])

    def update_uri_params(self, next_page_token: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None):
        offset = next_page_token.get("offset", 0) if next_page_token else 0
        stream_since = stream_state.get("modified_on", self.uri_params.get("since")) if stream_state else self.uri_params.get("since")
        self.uri_params.update(
            {
                "offset": int(offset),
                "since": stream_since
            }
        )


class IncrementalNettbutikk24Stream(Nettbutikk24Stream, ABC):
    state_checkpoint_interval = 1

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """

        return "modified_on"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        start_ts = self.uri_params.get("since")

        latest_record_modified_on = latest_record.get(self.cursor_field, "1970-01-01")
        latest_record_unix = convert_date_to_epoch(latest_record_modified_on)
        latest_record_unix = max(latest_record_unix, start_ts)

        stream_state = current_stream_state.get(self.cursor_field, 0)
        new_stream_state = max(stream_state, latest_record_unix)
        new_stream_state = min(int(pendulum.now().timestamp()), new_stream_state)

        return {self.cursor_field: new_stream_state}


class Products(IncrementalNettbutikk24Stream):
    primary_key = "id"

    # self.flat = False

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        self.update_uri_params(next_page_token, stream_state)
        self.uri_params.update({"limit": 10000})
        return "products/{limit}/{offset}/{since}".format_map(self.uri_params)

class Products_Flatted(IncrementalNettbutikk24Stream):
    primary_key = "id"

    # self.flat = False

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        self.update_uri_params(next_page_token, stream_state)
        self.uri_params.update({"limit": 10000})
        return "products/{limit}/{offset}/{since}".format_map(self.uri_params)


class Orders(IncrementalNettbutikk24Stream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        self.update_uri_params(next_page_token, stream_state)
        return "orders/{limit}/{offset}/{since}".format_map(self.uri_params)

class SourceNettbutikk24(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [Orders(config=config, flat = True), Products(config=config, flat = False), Products_Flatted(config=config, flat = True)]
