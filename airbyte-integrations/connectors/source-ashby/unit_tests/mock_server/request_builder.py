# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64
from typing import Any, Dict

from airbyte_cdk.test.mock_http import HttpRequest


class AshbyRequestBuilder:
    """
    Builder for Ashby API requests.

    Ashby's `.list` endpoints are POSTs that take their filters and pagination
    in the JSON body, so the builder accumulates body fields instead of query
    params. A Mapping body makes `HttpRequest.matches` compare bodies exactly.

    Example usage:
        request = (
            AshbyRequestBuilder.application_feedback_endpoint()
            .with_api_key("test-api-key")
            .with_created_after(1704067200000)
            .with_limit(100)
            .build()
        )
    """

    BASE_URL = "https://api.ashbyhq.com"

    def __init__(self, path: str) -> None:
        self._path = path
        self._headers: Dict[str, str] = {}
        self._body: Dict[str, Any] = {}

    @classmethod
    def application_feedback_endpoint(cls) -> "AshbyRequestBuilder":
        return cls("/applicationFeedback.list")

    def with_api_key(self, api_key: str) -> "AshbyRequestBuilder":
        """Set the Basic auth header the manifest's BasicHttpAuthenticator sends (key as user and password)."""
        token = base64.b64encode(f"{api_key}:{api_key}".encode()).decode()
        self._headers["Authorization"] = f"Basic {token}"
        return self

    def with_created_after(self, created_after_ms: int) -> "AshbyRequestBuilder":
        self._body["createdAfter"] = created_after_ms
        return self

    def with_limit(self, limit: int) -> "AshbyRequestBuilder":
        self._body["limit"] = limit
        return self

    def with_cursor(self, cursor: str) -> "AshbyRequestBuilder":
        self._body["cursor"] = cursor
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(url=f"{self.BASE_URL}{self._path}", headers=self._headers, body=dict(self._body))
