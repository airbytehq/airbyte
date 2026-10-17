# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Dict

from airbyte_cdk.test.mock_http import HttpRequest


class PostmarkRequestBuilder:
    BASE_URL = "https://api.postmarkapp.com"

    def __init__(self, path: str) -> None:
        self._path = path
        self._query_params: Dict[str, str] = {}

    @classmethod
    def messages_endpoint(cls) -> "PostmarkRequestBuilder":
        return cls("/messages/outbound")

    @classmethod
    def bounces_endpoint(cls) -> "PostmarkRequestBuilder":
        return cls("/bounces")

    @classmethod
    def servers_endpoint(cls) -> "PostmarkRequestBuilder":
        return cls("/servers")

    def with_pagination(self, count: int = 500, offset: int = 0) -> "PostmarkRequestBuilder":
        self._query_params["count"] = str(count)
        self._query_params["offset"] = str(offset)
        return self

    def with_interval(self, fromdate: str, todate: str) -> "PostmarkRequestBuilder":
        self._query_params["fromdate"] = fromdate
        self._query_params["todate"] = todate
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{self.BASE_URL}{self._path}",
            query_params=self._query_params,
            headers={"Accept": "application/json"},
        )
