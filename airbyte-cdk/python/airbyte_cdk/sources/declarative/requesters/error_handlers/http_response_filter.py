#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Set, Union

import requests
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from airbyte_cdk.sources.streams.http.http import HttpStream
from airbyte_cdk.sources.types import Config


@dataclass
class HttpResponseFilter:
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
    parameters: InitVar[Mapping[str, Any]]
    http_codes: Optional[Set[int]] = None
    error_message_contains: Optional[str] = None
    predicate: Union[InterpolatedBoolean, str] = ""
    error_message: Union[InterpolatedString, str] = ""

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if isinstance(self.action, str):
            self.action = ResponseAction[self.action]
        self.http_codes = self.http_codes or set()
        if isinstance(self.predicate, str):
            self.predicate = InterpolatedBoolean(condition=self.predicate, parameters=parameters)
        self.error_message = InterpolatedString.create(string_or_interpolated=self.error_message, parameters=parameters)

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
            response.status_code in self.http_codes  # type: ignore # http_codes set is always initialized to a value in __post_init__
            or (self._response_matches_predicate(response))
            or (self._response_contains_error_message(response))
        ):
            return self.action  # type: ignore # action is always cast to a ResponseAction not a str
        else:
            return None

    @staticmethod
    def _safe_response_json(response: requests.Response) -> dict[str, Any]:
        try:
            return response.json()  # type: ignore # Response.json() returns a dictionary even if the signature does not
        except requests.exceptions.JSONDecodeError:
            return {}

    def _create_error_message(self, response: requests.Response) -> str:
        """
        Construct an error message based on the specified message template of the filter.
        :param response: The HTTP response which can be used during interpolation
        :return: The evaluated error message string to be emitted
        """
        return self.error_message.eval(self.config, response=self._safe_response_json(response), headers=response.headers)  # type: ignore # error_message is always cast to an interpolated string

    def _response_matches_predicate(self, response: requests.Response) -> bool:
        return bool(self.predicate and self.predicate.eval(None, response=self._safe_response_json(response), headers=response.headers))  # type: ignore # predicate is always cast to an interpolated string

    def _response_contains_error_message(self, response: requests.Response) -> bool:
        if not self.error_message_contains:
            return False
        else:
            error_message = HttpStream.parse_response_error_message(response)
            return bool(error_message and self.error_message_contains in error_message)
