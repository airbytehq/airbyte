# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


class OAuthResponseBuilder:
    @classmethod
    def token_response(cls, status_code: int = 200) -> "OAuthResponseBuilder":
        return cls("oauth", status_code)

    def __init__(self, resource: str, status_code: int = 200) -> None:
        self._status_code: int = status_code
        self._resource: str = resource

    def with_status_code(self, status_code: int) -> "OAuthResponseBuilder":
        self._status_code = status_code
        return self

    def build(self) -> HttpResponse:
        return HttpResponse(json.dumps(find_template(self._resource, __file__)), self._status_code)
