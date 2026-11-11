# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional

from airbyte_cdk.test.mock_http import HttpRequest


API_BASE_URL = "https://api.mention.net/api"


class MentionRequestBuilder:
    """Builder for requests the source-mention connector sends to the Mention API."""

    @classmethod
    def account_me_endpoint(cls) -> "MentionRequestBuilder":
        return cls("accounts/me")

    @classmethod
    def alerts_endpoint(cls, account_id: str) -> "MentionRequestBuilder":
        return cls(f"accounts/{account_id}/alerts")

    def __init__(self, resource: str) -> None:
        self._resource = resource
        self._query_params: Dict[str, Any] = {}
        self._headers: Optional[Dict[str, str]] = None

    def with_query_param(self, key: str, value: Any) -> "MentionRequestBuilder":
        self._query_params[key] = value
        return self

    def with_authorization(self, value: str) -> "MentionRequestBuilder":
        self._headers = {"Authorization": value}
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{API_BASE_URL}/{self._resource}",
            query_params=self._query_params or None,
            headers=self._headers,
        )
