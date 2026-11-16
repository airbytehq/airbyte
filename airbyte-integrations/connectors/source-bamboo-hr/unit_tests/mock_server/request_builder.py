# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


class BambooHrRequestBuilder:
    def __init__(self, path: str) -> None:
        self._path = path
        self._params = {}

    def with_query_param(self, name: str, value: str) -> "BambooHrRequestBuilder":
        self._params[name] = value
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"https://api.bamboohr.com/api/gateway.php/test-company/v1/{self._path}",
            query_params=self._params,
        )
