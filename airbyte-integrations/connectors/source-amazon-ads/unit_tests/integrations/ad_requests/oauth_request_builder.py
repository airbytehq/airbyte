# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional

from .base_request_builder import AmazonAdsRequestBuilder
from .constants import BASE_OAUTH_URL


class OAuthRequestBuilder(AmazonAdsRequestBuilder):
    @classmethod
    def oauth_endpoint(cls, client_id: str, client_secred: str, refresh_token: str) -> "OAuthRequestBuilder":
        return cls("auth/o2/token").with_client_id(client_id).with_client_secret(client_secred).with_refresh_token(refresh_token)

    def __init__(self, resource: str) -> None:
        self._resource: str = resource
        self._client_id: str = None
        self._client_secret: str = None
        self._refresh_token: str = None

    @property
    def url(self) -> str:
        return f"{BASE_OAUTH_URL}/{self._resource}"

    @property
    def query_params(self) -> Dict[str, Any]:
        return {}

    @property
    def headers(self) -> Dict[str, Any]:
        return {}

    @property
    def request_body(self) -> Optional[str]:
        return (
            f"grant_type=refresh_token&client_id={self._client_id}&client_secret={self._client_secret}&refresh_token={self._refresh_token}"
        )

    def with_client_id(self, client_id: str) -> "OAuthRequestBuilder":
        self._client_id: str = client_id
        return self

    def with_client_secret(self, client_secret: str) -> "OAuthRequestBuilder":
        self._client_secret: str = client_secret
        return self

    def with_refresh_token(self, refresh_token: str) -> "OAuthRequestBuilder":
        self._refresh_token: str = refresh_token
        return self
