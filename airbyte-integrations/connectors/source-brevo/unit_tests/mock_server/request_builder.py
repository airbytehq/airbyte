# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


class BrevoRequestBuilder:
    def __init__(self, path: str) -> None:
        self._path = path
        self._query: dict[str, str] = {}

    def with_query_params(self, **params: str | int) -> "BrevoRequestBuilder":
        self._query.update({key: str(value) for key, value in params.items()})
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"https://api.brevo.com/v3/{self._path}",
            query_params=self._query,
            headers={"api-key": "test-api-key"},
        )
