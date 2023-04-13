#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import pendulum
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class MinnesiderStream(HttpStream, ABC):
    url_base = "https://api.minnesider.no/api/web/portal/v2/"

    def __init__(self, config):
        super().__init__()
        self.start_date = config.get('start_date')
        self.params = {
            "page": 0,
            "size": 100,
            "domain": "minnesider.no",
            "area": "local",
            "deathDate": self.start_date
        }

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
        if response.status_code == 500:
            self.params.update(
                {
                    "page": 0,
                    "deathDate": pendulum.parse(self.params["deathDate"]).add(days=1).format("YYYY-MM-DD")
                }
            )
            return {"next": True}


        response_data = response.json()
        is_last_page = response_data.get("last")

        if is_last_page:
            self.params.update(
                {
                    "page": 0,
                    "deathDate": pendulum.parse(self.params["deathDate"]).add(days=1).format("YYYY-MM-DD")
                }
            )
        else:
            self.params.update({"page": self.params["page"] + 1})

        if pendulum.parse(self.params["deathDate"]) > pendulum.now():
            return None

        else:
            return {"next": True}

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        state_date = pendulum.parse(stream_state.get('deathDate', self.start_date)).subtract(days = 14)

        if state_date > pendulum.parse(self.params.get('deathDate')):
            self.params.update(
                {
                    "page": 0,
                    "deathDate": state_date.format("YYYY-MM-DD")
                }
            )

        print("=" * 100)
        print(self.params)
        print("=" * 100)

        return self.params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        if response.status_code == 500:
            yield from []

        yield from response.json().get("content", [])

    @property
    def raise_on_http_errors(self) -> bool:
        """
        Override if needed. If set to False, allows opting-out of raising HTTP code exception.
        """
        return False

    def should_retry(self, response: requests.Response) -> bool:
        return response.status_code == 429 or 500 < response.status_code < 600


# Basic incremental stream
class IncrementalMinnesiderStream(MinnesiderStream, ABC):
    state_checkpoint_interval = 1

    @property
    def cursor_field(self) -> str:
        """
        :return str: The name of the cursor field.
        """
        return 'deathDate'

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        last_record_date = pendulum.parse(latest_record.get("deathDate"))
        last_stream_date = pendulum.parse(current_stream_state.get(self.cursor_field, self.start_date))
        last_date = max(last_stream_date, last_record_date).format("YYYY-MM-DD")
        return {self.cursor_field: last_date}


class Search(IncrementalMinnesiderStream):
    primary_key = "id"
    cursor_field = "deathDate"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "search"


class SourceMinnesider(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [Search(config)]
