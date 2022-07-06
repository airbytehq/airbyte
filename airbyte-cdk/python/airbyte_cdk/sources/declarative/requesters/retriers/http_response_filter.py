#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

import requests
from airbyte_cdk.sources.streams.http.http import HttpStream
from pydantic import BaseModel


class HttpResponseFilter(BaseModel):
    TOO_MANY_REQUESTS_ERRORS = set([429])
    DEFAULT_RETRIABLE_ERRORS = set([x for x in range(500, 600)]).union(TOO_MANY_REQUESTS_ERRORS)

    http_codes: List[int] = []
    predicate: Optional[str] = None
    error_message_contains: Optional[str] = None

    # def __init__(self, http_codes: Set[int] = None, error_message_contain: str = None, predicate: str = ""):
    #    self._http_codes = http_codes or HttpResponseFilter.DEFAULT_RETRIABLE_ERRORS
    #    self._predicate = InterpolatedBoolean(predicate)
    #    self._error_message_contains = error_message_contain

    def matches(self, response: requests.Response) -> bool:
        return (
            response.status_code in self.http_codes
            or (self._response_matches_predicate(response))
            or (self._response_contains_error_message(response))
        )

    def _response_matches_predicate(self, response: requests.Response) -> bool:
        return self.predicate and self.predicate.eval(None, decoded_response=response.json())

    def _response_contains_error_message(self, response: requests.Response) -> bool:
        if not self.error_message_contains:
            return False
        else:
            return self.error_message_contains in HttpStream.parse_response_error_message(response)
