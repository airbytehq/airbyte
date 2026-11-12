# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Dict

from airbyte_cdk.test.mock_http import HttpRequest


class NylasRequestBuilder:
    """Builder for Nylas v3 API requests on the US server, authenticated with the test API key."""

    BASE_URL = "https://api.us.nylas.com"
    PAGE_SIZE = "50"

    def __init__(self, path: str) -> None:
        self._path = path
        self._query_params: Dict[str, str] = {"limit": self.PAGE_SIZE}

    @classmethod
    def grants_endpoint(cls) -> "NylasRequestBuilder":
        return cls("/v3/grants")

    @classmethod
    def calendars_endpoint(cls, grant_id: str) -> "NylasRequestBuilder":
        return cls(f"/v3/grants/{grant_id}/calendars")

    @classmethod
    def events_endpoint(cls, grant_id: str) -> "NylasRequestBuilder":
        return cls(f"/v3/grants/{grant_id}/events")

    def with_query_param(self, key: str, value: str) -> "NylasRequestBuilder":
        self._query_params[key] = value
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{self.BASE_URL}{self._path}",
            query_params=dict(self._query_params),
            headers={"Authorization": "Bearer test-api-key"},
        )
