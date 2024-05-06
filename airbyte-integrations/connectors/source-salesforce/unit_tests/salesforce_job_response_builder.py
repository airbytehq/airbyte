# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, find_template


class JobCreateResponseBuilder:
    def __init__(self):
        self._response = {
           "id": "any_id",
           "operation": "query",
           "object": "Account",
           "createdById": "005R0000000GiwjIAC",
           "createdDate": "2018-12-17T21:00:17.000+0000",
           "systemModstamp": "2018-12-17T21:00:17.000+0000",
           "state": "UploadComplete",
           "concurrencyMode": "Parallel",
           "contentType": "CSV",
           "apiVersion": 46.0,
           "lineEnding": "LF",
           "columnDelimiter": "COMMA"
        }
        self._status_code = 200

    def with_id(self, id: str) -> "JobCreateResponseBuilder":
        self._response["id"] = id
        return self

    def with_state(self, state: str) -> "JobCreateResponseBuilder":
        self._response["state"] = state
        return self

    def build(self) -> HttpResponse:
        return HttpResponse(json.dumps(self._response), self._status_code)


class JobInfoResponseBuilder:
    def __init__(self):
        self._response = find_template("job_response", __file__)
        self._status_code = 200

    def with_id(self, id: str) -> "JobInfoResponseBuilder":
        self._response["id"] = id
        return self

    def with_state(self, state: str) -> "JobInfoResponseBuilder":
        self._response["state"] = state
        return self

    def with_status_code(self, status_code: int) -> "JobInfoResponseBuilder":
        self._status_code = status_code
        return self
    
    def with_error_message(self, error_message: str) -> "JobInfoResponseBuilder":
        self._response["errorMessage"] = error_message
        return self
    
    def get_response(self) -> any:
        return self._response

    def build(self) -> HttpResponse:
        return HttpResponse(json.dumps(self._response), self._status_code)
