from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class WaitwhileStream(HttpStream, ABC):
    url_base = "https://api.waitwhile.com/v2/"
    primary_key = None
    limit = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        end_at = response.json()["endAt"]

        if end_at:
            end_at = end_at.split(",")[-1]
            return {"startAfter": end_at}

        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.limit, "desc": False}
        if next_page_token:
            params.update(**next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        if response.status_code != 200:
            return []

        response_json = response.json().get("results")
        if response_json:
            yield from response_json

        return []


class IncrementalWaitwhileStream(WaitwhileStream, ABC):
    state_checkpoint_interval = 10

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return "endAt"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        last_cursor_value = latest_record.get(self.cursor_field)
        if last_cursor_value:
            return {self.cursor_field: last_cursor_value}

        return current_stream_state or {}


class Locations(IncrementalWaitwhileStream):
    """
    List locations data source.
    """

    cursor_field = "startAt"
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "locations"


class Services(IncrementalWaitwhileStream):
    """
    List services data source.
    """

    cursor_field = "startAt"
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "services"


class Resources(IncrementalWaitwhileStream):
    """
    List resources data source.
    """

    cursor_field = "startAt"
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "resources"


class Users(IncrementalWaitwhileStream):
    """
    List users data source.
    """

    cursor_field = "startAt"
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "users"


class LocationStatus(IncrementalWaitwhileStream):
    """
    List location status data source.
    """

    cursor_field = "startAt"
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "location-status"



class SourceWaitwhile(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        try:
            headers = dict(Accept="application/json", apikey=config["apikey"])
            url = "https://api.waitwhile.com/v2/"
            session = requests.get(url, headers=headers)
            session.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = TokenAuthenticator(config["apikey"])
        return [
            Locations(authenticator=auth),
            Services(authenticator=auth),
            Resources(authenticator=auth),
            Users(authenticator=auth),
            LocationStatus(authenticator=auth),
            # Customers(authenticator=auth),
            # Visits(authenticator=auth),
        ]
