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

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""


# Basic full refresh stream
class EnquireLabsStream(HttpStream, ABC):

    primary_key = None
    url_base = "https://app.enquirelabs.com/api/"

    def __init__(self, secret_key, **kwargs):
        super().__init__(**kwargs)
        self.secret_key = secret_key

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Authorization": self.secret_key}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Returns:
            request response
        """
        return [response.json()]

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "questions"


class QuestionStream(EnquireLabsStream):
    primary_key = None

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
        params = {
            "since": self.since,
            "until": self.until,
            "question_id": self.question_id
        }
        params.update(next_page_token)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if decoded_response.get("next"):
            return {"after": decoded_response.get("data").get("response_id")}

        return None


class IncrementalEnquireLabsStream(EnquireLabsStream, ABC):

    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
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
            validator = True, None
        except Exception as e:
            validator = False, e

        return validator

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Args:
            config: A Mapping of the user input configuration as defined in the connector spec.
        Returns:
             list: list of streams
        """

        args = {
            "secret_key": config["secret_key"],
            "since": config.get("since"),
            "until": config.get("until"),
            "question_id": config.get("question_id")
        }
        return [QuestionStream(secret_key=config["secret_key"]), QuestionResponseStream(**args)]
