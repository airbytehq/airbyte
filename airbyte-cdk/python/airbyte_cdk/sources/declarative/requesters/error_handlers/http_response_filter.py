#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Set, Union

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
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
    """

    TOO_MANY_REQUESTS_ERRORS = {429}
    DEFAULT_RETRIABLE_ERRORS = set([x for x in range(500, 600)]).union(TOO_MANY_REQUESTS_ERRORS)

    action: Union[ResponseAction, str]
    options: InitVar[Mapping[str, Any]]
    http_codes: Set[int] = None
    error_message_contains: str = None
    predicate: Union[InterpolatedBoolean, str] = ""

    def __post_init__(self, options: Mapping[str, Any]):
        if isinstance(self.action, str):
            self.action = ResponseAction[self.action]
        self.http_codes = self.http_codes or set()
        if isinstance(self.predicate, str):
            self.predicate = InterpolatedBoolean(condition=self.predicate, options=options)

    def matches(self, response: requests.Response) -> Optional[ResponseAction]:
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

    def _response_matches_predicate(self, response: requests.Response) -> bool:
        return self.predicate and self.predicate.eval(None, response=response.json(), headers=response.headers)

    def _response_contains_error_message(self, response: requests.Response) -> bool:
        if not self.error_message_contains:
            return False
        else:
            error_message = HttpStream.parse_response_error_message(response)
            return error_message and self.error_message_contains in error_message
