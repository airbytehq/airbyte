# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Dict, Optional

from airbyte_cdk.test.mock_http import HttpRequest


API_PREFIX = "/v2"
BASE_URL = f"https://api.revenuecat.com{API_PREFIX}"
PAGE_SIZE = "100"


class RevenueCatRequestBuilder:
    """Builds the requests the connector sends to the RevenueCat v2 API."""

    def __init__(self, path: str) -> None:
        self._path = path
        self._query_params: Dict[str, str] = {"limit": PAGE_SIZE}

    @classmethod
    def endpoint(cls, path: str) -> "RevenueCatRequestBuilder":
        return cls(path)

    def with_starting_after(self, starting_after: str) -> "RevenueCatRequestBuilder":
        self._query_params["starting_after"] = starting_after
        return self

    def without_query_params(self) -> "RevenueCatRequestBuilder":
        self._query_params = {}
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(url=f"{BASE_URL}{self._path}", query_params=dict(self._query_params) or None)


def next_page_path(path: str, starting_after_encoded: str, extra: Optional[str] = None) -> str:
    """Return a `next_page` value the way RevenueCat returns it: an API-relative path with an already-encoded cursor."""
    query = f"starting_after={starting_after_encoded}"
    if extra:
        query = f"{query}&{extra}"
    return f"{API_PREFIX}{path}?{query}"
