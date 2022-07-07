#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Set

import requests
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.streams.http.http import HttpStream


class HttpResponseFilter:
    TOO_MANY_REQUESTS_ERRORS = set([429])
    DEFAULT_RETRIABLE_ERRORS = set([x for x in range(500, 600)]).union(TOO_MANY_REQUESTS_ERRORS)

    def __init__(self, http_codes: Set[int] = None, error_message_contain: str = None, predicate: str = ""):
        self._http_codes = http_codes or set()
        self._predicate = InterpolatedBoolean(predicate)
        self._error_message_contains = error_message_contain

    def matches(self, response: requests.Response) -> bool:
        return (
            response.status_code in self._http_codes
            or (self._response_matches_predicate(response))
            or (self._response_contains_error_message(response))
        )

    def _response_matches_predicate(self, response: requests.Response) -> bool:
        return self._predicate and self._predicate.eval(None, decoded_response=response.json())

    def _response_contains_error_message(self, response: requests.Response) -> bool:
        if not self._error_message_contains:
            return False
        else:
            return self._error_message_contains in HttpStream.parse_response_error_message(response)
