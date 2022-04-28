from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import datetime
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
        Returns:request response
        """
        json_response = response.json()
        for record in json_response.get("data"):
            yield record


class IncrementalEnquireLabsStream(EnquireLabsStream, ABC):

    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        pass

    def _convert_date_to_timestamp(self, date: datetime):
        return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S+00:00")

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        base_date = (
            datetime.datetime.combine(
                datetime.date.fromtimestamp(0),
                datetime.datetime.min.time()
            ).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        )
        state_dt = self._convert_date_to_timestamp(current_stream_state.get(self.cursor_field, base_date))
        latest_record = self._convert_date_to_timestamp(latest_record.get(self.cursor_field, base_date))

        return {self.cursor_field: max(latest_record, state_dt)}


class QuestionStream(IncrementalEnquireLabsStream):
    primary_key = "id"
    cursor_field = "inserted_at"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        """
        Ref: https://docs.enquirelabs.com/docs

        Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"
        """
        return "questions"


class QuestionResponseStream(IncrementalEnquireLabsStream):
    """
    This stream is currently not working because of their internal server error

    Ref: https://docs.enquirelabs.com/reference/retrieve-responses

    please add this stream when it's available
    """
    primary_key = "id"
    cursor_field = "inserted_at"

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
        """
        Ref: https://docs.enquirelabs.com/docs

        Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"
        """
        return "responses"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Ref: https://docs.enquirelabs.com/docs
        Adds query params in requested URL.
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
        """
        Ref: https://docs.enquirelabs.com/docs
        Implements the pagination approach for stream.

        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """
        decoded_response = response.json()
        if decoded_response.get("next"):
            return {"after": decoded_response.get("data")[0]["response_id"] if decoded_response.get("data") else None}


class SourceEnquireLabs(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        try:
            QuestionStream(secret_key=config["secret_key"])
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
        return [QuestionStream(secret_key=config["secret_key"])]
