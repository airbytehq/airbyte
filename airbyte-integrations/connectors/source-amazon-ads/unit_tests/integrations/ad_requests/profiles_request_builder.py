# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Optional

from .base_request_builder import AmazonAdsRequestBuilder
from .constants import BASE_URL


class ProfilesRequestBuilder(AmazonAdsRequestBuilder):
    @classmethod
    def profiles_endpoint(cls, client_id: str, client_access_token: str) -> "ProfilesRequestBuilder":
        return cls("v2/profiles") \
            .with_client_id(client_id) \
            .with_client_access_token(client_access_token) \
            .with_profile_type_filter(["seller", "vendor"])

    def __init__(self, resource: str) -> None:
        self._resource: str = resource
        self._client_id: str = None
        self._client_access_token: str = None
        self._profile_type_filter: Optional[List[str]] = None

    @property
    def url(self) -> str:
        url = f"{BASE_URL}/{self._resource}"
        if self._profile_type_filter:
             url = f"{url}?profileTypeFilter={','.join(self._profile_type_filter)}"
        return url

    @property
    def query_params(self) -> Dict[str, Any]:
        return {}

    @property
    def headers(self) -> Dict[str, Any]:
        return {
            "Amazon-Advertising-API-ClientId": self._client_id,
            "Authorization": f"Bearer {self._client_access_token}",
        }

    @property
    def request_body(self) -> Optional[str]:
        return None

    def with_profile_type_filter(self, profile_type_filter: List[str]) -> "ProfilesRequestBuilder":
        self._profile_type_filter: List[str] = profile_type_filter
        return self

    def with_client_id(self, client_id: str) -> "ProfilesRequestBuilder":
        self._client_id: str = client_id
        return self

    def with_client_access_token(self, client_access_token: str) -> "ProfilesRequestBuilder":
        self._client_access_token: str = client_access_token
        return self
