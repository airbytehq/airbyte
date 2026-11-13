# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import urlencode

from airbyte_cdk.test.mock_http import HttpRequest


BASE_URL = "https://api.outreach.io/api/v2"
TOKEN_URL = "https://api.outreach.io/oauth/token"
# The connector sends the start date in the cursor format, with milliseconds.
START_CURSOR = "2020-11-16T00:00:00.000Z"


class OutreachRequestBuilder:
    """Builds the list request every stream sends: sorted by `updatedAt`, filtered from a cursor."""

    @classmethod
    def endpoint(cls, path: str) -> "OutreachRequestBuilder":
        return cls(path)

    @staticmethod
    def token_request() -> HttpRequest:
        return HttpRequest(
            TOKEN_URL,
            body="grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token",
        )

    def __init__(self, path: str) -> None:
        self._path = path
        self._page_size = 1000
        self._updated_since = START_CURSOR

    def with_page_size(self, page_size: int) -> "OutreachRequestBuilder":
        self._page_size = page_size
        return self

    def with_updated_since(self, cursor: str) -> "OutreachRequestBuilder":
        self._updated_since = cursor
        return self

    def _query_params(self) -> dict[str, str]:
        return {
            "count": "false",
            "sort": "updatedAt",
            "page[size]": str(self._page_size),
            "newFilterSyntax": "true",
            "filter[updatedAt][gte]": self._updated_since,
        }

    def build(self) -> HttpRequest:
        return HttpRequest(f"{BASE_URL}{self._path}", query_params=self._query_params())

    def next_page_url(self, page_after: str) -> str:
        """The `links.next` URL Outreach returns: the same query plus an opaque `page[after]` cursor."""
        return f"{BASE_URL}{self._path}?{urlencode({**self._query_params(), 'page[after]': page_after})}"
