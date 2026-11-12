# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

from airbyte_cdk.test.mock_http import HttpRequest


class NylasRequestBuilder:
    """Builder for Nylas v3 API GET requests (cursor pagination via `page_token`/`limit` query params)."""

    BASE_URL = "https://api.us.nylas.com"

    def __init__(self, path: str) -> None:
        self._path = path
        self._query_params: Dict[str, Any] = {}

    @classmethod
    def grants_endpoint(cls) -> "NylasRequestBuilder":
        return cls("/v3/grants")

    @classmethod
    def calendars_endpoint(cls, grant_id: str) -> "NylasRequestBuilder":
        return cls(f"/v3/grants/{grant_id}/calendars")

    @classmethod
    def events_endpoint(cls, grant_id: str) -> "NylasRequestBuilder":
        return cls(f"/v3/grants/{grant_id}/events")

    def with_limit(self, limit: int) -> "NylasRequestBuilder":
        self._query_params["limit"] = str(limit)
        return self

    def with_query_param(self, key: str, value: Any) -> "NylasRequestBuilder":
        self._query_params[key] = str(value)
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{self.BASE_URL}{self._path}",
            query_params=self._query_params or None,
            headers={"Authorization": "Bearer test-api-key"},
        )
