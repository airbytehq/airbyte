# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Dict

from airbyte_cdk.test.mock_http import HttpRequest


class MentionRequestBuilder:
    """
    Builder for Mention API requests.

    The builder always pins the query string (an empty dict when none is set), so a
    request with unexpected parameters does not match. `with_access_token` pins the
    `Authorization` header as well.
    """

    BASE_URL = "https://api.mention.net/api"

    def __init__(self, path: str) -> None:
        self._path = path
        self._headers: Dict[str, str] = {}
        self._query_params: Dict[str, str] = {}

    @classmethod
    def account_me_endpoint(cls) -> "MentionRequestBuilder":
        return cls("/accounts/me")

    @classmethod
    def alerts_endpoint(cls, account_id: str) -> "MentionRequestBuilder":
        return cls(f"/accounts/{account_id}/alerts")

    def with_access_token(self, access_token: str) -> "MentionRequestBuilder":
        """Set the `Authorization: Bearer <token>` header that the Mention API requires."""
        self._headers["Authorization"] = f"Bearer {access_token}"
        return self

    def with_limit(self, limit: int) -> "MentionRequestBuilder":
        self._query_params["limit"] = str(limit)
        return self

    def with_cursor(self, cursor: str) -> "MentionRequestBuilder":
        self._query_params["cursor"] = cursor
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{self.BASE_URL}{self._path}",
            query_params=self._query_params,
            headers=self._headers or None,
        )
