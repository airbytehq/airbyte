# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


class SalesloftRequestBuilder:
    def __init__(self, token: str) -> None:
        self._token = token
        self._params = {"per_page": "100"}

    @classmethod
    def users(cls, token: str) -> "SalesloftRequestBuilder":
        return cls(token)

    def with_page(self, page: int) -> "SalesloftRequestBuilder":
        self._params["page"] = str(page)
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url="https://api.salesloft.com/v2/users",
            query_params=self._params,
            headers={"Authorization": f"Bearer {self._token}"},
        )
