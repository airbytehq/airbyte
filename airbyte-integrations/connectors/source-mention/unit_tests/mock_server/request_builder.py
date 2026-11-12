# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional

from airbyte_cdk.test.mock_http import HttpRequest


class MentionRequestBuilder:
    BASE_URL = "https://api.mention.net/api"

    @classmethod
    def account_me_endpoint(cls, api_key: str) -> "MentionRequestBuilder":
        return cls("accounts/me", api_key)

    @classmethod
    def alerts_endpoint(cls, api_key: str, account_id: str) -> "MentionRequestBuilder":
        return cls(f"accounts/{account_id}/alerts", api_key)

    def __init__(self, resource: str, api_key: str) -> None:
        self._resource = resource
        self._api_key = api_key
        self._query_params: Dict[str, Any] = {}

    def with_query_param(self, key: str, value: Any) -> "MentionRequestBuilder":
        self._query_params[key] = value
        return self

    def build(self) -> HttpRequest:
        query_params: Optional[Dict[str, Any]] = self._query_params or None
        return HttpRequest(
            url=f"{self.BASE_URL}/{self._resource}",
            query_params=query_params,
            headers={"Authorization": f"Bearer {self._api_key}"},
        )
