# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


class NylasRequestBuilder:
    def __init__(self, path: str) -> None:
        self._path = path
        self._query_params = {"limit": "50"}

    def with_query_param(self, key: str, value: str) -> "NylasRequestBuilder":
        self._query_params[key] = value
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"https://api.us.nylas.com/v3/{self._path}",
            headers={"Authorization": "Bearer test-api-key"},
            query_params=dict(self._query_params),
        )
