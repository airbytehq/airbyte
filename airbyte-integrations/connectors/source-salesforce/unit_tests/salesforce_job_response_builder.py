# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, find_template


class SalesforceJobResponseBuilder:
    def __init__(self):
        self._response = find_template("job_response", __file__)
        self._status_code = 200

    def with_id(self, id: str) -> "HttpResponseBuilder":
        self._response["id"] = id
        return self

    def with_state(self, state: str) -> "HttpResponseBuilder":
        self._response["state"] = state
        return self

    def with_status_code(self, status_code: int) -> "HttpResponseBuilder":
        self._status_code = status_code
        return self
    
    def with_error_message(self, error_message: int) -> "HttpResponseBuilder":
        self._response["errorMessage"] = error_message
        return self
    
    def get_response(self) -> any:
        return self._response

    def build(self) -> HttpResponse:
        return HttpResponse(json.dumps(self._response), self._status_code)
    