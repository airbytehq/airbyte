#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator


# Basic full refresh stream
class HubplannerStream(HttpStream, ABC):

    url_base = "https://api.hubplanner.com/v1"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield {}


# Basic incremental stream
class IncrementalHubplannerStream(HubplannerStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class HubplannerAuthenticator(HttpAuthenticator):
    def __init__(self, token: str, auth_header: str = "Authorization"):
        self.auth_header = auth_header
        self._token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f"{self._token}"}


class BillingRates(HubplannerStream):
    primary_key = "_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v1/billingRate"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return super().request_params(stream_state, stream_slice, next_page_token)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()


class Bookings(HubplannerStream):
    primary_key = "_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v1/booking"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return super().request_params(stream_state, stream_slice, next_page_token)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()


class Clients(HubplannerStream):
    primary_key = "_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v1/client"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return super().request_params(stream_state, stream_slice, next_page_token)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()


class Events(HubplannerStream):
    primary_key = "_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v1/event"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return super().request_params(stream_state, stream_slice, next_page_token)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()


class Holidays(HubplannerStream):
    primary_key = "_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v1/holiday"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return super().request_params(stream_state, stream_slice, next_page_token)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()


class Projects(HubplannerStream):
    primary_key = "_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v1/project"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return super().request_params(stream_state, stream_slice, next_page_token)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()


class Resources(HubplannerStream):
    primary_key = "_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "v1/resource"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return super().request_params(stream_state, stream_slice, next_page_token)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()


# Source
class SourceHubplanner(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        url_base = "https://api.hubplanner.com/v1"

        try:
            url = f"{url_base}/project"

            authenticator = HubplannerAuthenticator(token=config["api_key"])

            session = requests.get(url, headers=authenticator.get_auth_header())
            session.raise_for_status()

            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        authenticator = HubplannerAuthenticator(token=config["api_key"])
        return [
            BillingRates(authenticator=authenticator),
            Bookings(authenticator=authenticator),
            Clients(authenticator=authenticator),
            Events(authenticator=authenticator),
            Holidays(authenticator=authenticator),
            Projects(authenticator=authenticator),
            Resources(authenticator=authenticator),
        ]
