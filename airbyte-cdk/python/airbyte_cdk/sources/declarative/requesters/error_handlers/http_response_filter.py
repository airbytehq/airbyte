#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Set, Union

import requests
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.streams.http.http import HttpStream
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class HttpResponseFilter(JsonSchemaMixin):
    """
    Filter to select HttpResponses

    Attributes:
        action (Union[ResponseAction, str]): action to execute if a request matches
        http_codes (Set[int]): http code of matching requests
        error_message_contains (str): error substring of matching requests
        predicate (str): predicate to apply to determine if a request is matching
        error_message (Union[InterpolatedString, str): error message to display if the response matches the filter
    """

    TOO_MANY_REQUESTS_ERRORS = {429}
    DEFAULT_RETRIABLE_ERRORS = set([x for x in range(500, 600)]).union(TOO_MANY_REQUESTS_ERRORS)

    action: Union[ResponseAction, str]
    config: Config
    options: InitVar[Mapping[str, Any]]
    http_codes: Set[int] = None
    error_message_contains: str = None
    predicate: Union[InterpolatedBoolean, str] = ""
    error_message: Union[InterpolatedString, str] = ""

    def __post_init__(self, options: Mapping[str, Any]):
        if isinstance(self.action, str):
            self.action = ResponseAction[self.action]
        self.http_codes = self.http_codes or set()
        if isinstance(self.predicate, str):
            self.predicate = InterpolatedBoolean(condition=self.predicate, options=options)
        self.error_message = InterpolatedString.create(string_or_interpolated=self.error_message, options=options)

    def matches(self, response: requests.Response, backoff_time: Optional[float] = None) -> Optional[ResponseStatus]:
        filter_action = self._matches_filter(response)
        if filter_action is not None:
            error_message = self._create_error_message(response)
            if filter_action == ResponseAction.RETRY:
                return ResponseStatus(
                    response_action=ResponseAction.RETRY,
                    retry_in=backoff_time,
                    error_message=error_message,
                )
            else:
                return ResponseStatus(filter_action, error_message=error_message)
        return None

    def _matches_filter(self, response: requests.Response) -> Optional[ResponseAction]:
        """
        Apply the filter on the response and return the action to execute if it matches
        :param response: The HTTP response to evaluate
        :return: The action to execute. None if the response does not match the filter
        """
        if (
            response.status_code in self.http_codes
            or (self._response_matches_predicate(response))
            or (self._response_contains_error_message(response))
        ):
            return self.action
        else:
            return None

    @staticmethod
    def _safe_response_json(response: requests.Response) -> dict:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return {}

    def _create_error_message(self, response: requests.Response) -> str:
        """
        Construct an error message based on the specified message template of the filter.
        :param response: The HTTP response which can be used during interpolation
        :return: The evaluated error message string to be emitted
        """
        return self.error_message.eval(self.config, response=self._safe_response_json(response), headers=response.headers)

    def _response_matches_predicate(self, response: requests.Response) -> bool:
        return self.predicate and self.predicate.eval(None, response=self._safe_response_json(response), headers=response.headers)

    def _response_contains_error_message(self, response: requests.Response) -> bool:
        if not self.error_message_contains:
            return False
        else:
            error_message = HttpStream.parse_response_error_message(response)
            return error_message and self.error_message_contains in error_message
