#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class EnquireLabsStream(HttpStream, ABC):

    primary_key = None
    url_base = "https://app.enquirelabs.com/api/"

    def __init__(self, secret_key, **kwargs):
        super().__init__(**kwargs)
        self.secret_key = secret_key

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
        return None

    def request_headers(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override this function to add header in your request

        Returns:
            dict: object of headers
        """
        return {"Authorization": self.secret_key}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Returns:
            request response
        """
        return [response.json()]


class QuestionStream(EnquireLabsStream):
    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:

        return "questions"


class QuestionResponseStream(EnquireLabsStream):
    def __init__(self, secret_key, since, until, question_id, **kwargs):
        super().__init__(secret_key=secret_key, **kwargs)
        self.since = since
        self.until = until
        self.question_id = question_id

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "responses"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        This method use to add query params in requested URL
        """
        params = {
            "since": self.since,
            "until": self.until,
            "question_id": self.question_id
        }

        if next_page_token:
            params.update(next_page_token)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if decoded_response.get("next"):
            return {"after": decoded_response.get("data")[0]["response_id"] if decoded_response.get("data") else None}

        return None


class IncrementalEnquireLabsStream(EnquireLabsStream, ABC):

    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
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


# Source
class SourceEnquireLabs(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        url = "https://app.enquirelabs.com/api/questions"

        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': config["secret_key"]
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            connection = True, None
        except Exception as e:
            connection = False, e

        return connection

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        args = {
            "secret_key": config["secret_key"],
            "since": config.get("since"),
            "until": config.get("until"),
            "question_id": config.get("question_id")
        }
        return [QuestionStream(secret_key=config["secret_key"]), QuestionResponseStream(**args)]
