# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Dict

from airbyte_cdk.test.mock_http import HttpRequest


class NylasRequestBuilder:
    BASE_URL = "https://api.us.nylas.com"

    def __init__(self, path: str) -> None:
        self._path = path
        self._query_params: Dict[str, str] = {"limit": "50"}

    @classmethod
    def endpoint(cls, path: str) -> "NylasRequestBuilder":
        return cls(path)

    def with_query_param(self, key: str, value: str) -> "NylasRequestBuilder":
        self._query_params[key] = value
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{self.BASE_URL}{self._path}",
            query_params=dict(self._query_params),
            headers={"Authorization": "Bearer test-api-key"},
        )
