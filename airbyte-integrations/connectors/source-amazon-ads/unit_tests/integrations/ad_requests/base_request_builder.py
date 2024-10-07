# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import abc
from typing import Any, Dict, Optional

from airbyte_cdk.test.mock_http import HttpRequest

from .constants import BASE_URL


class AmazonAdsRequestBuilder(abc.ABC):
    @property
    @abc.abstractmethod
    def url(self) -> str:
        """"""

    @property
    @abc.abstractmethod
    def query_params(self) -> Dict[str, Any]:
        """"""

    @property
    @abc.abstractmethod
    def headers(self) -> Dict[str, Any]:
        """"""

    @property
    @abc.abstractmethod
    def request_body(self) -> Optional[str]:
        """"""

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=self.url,
            query_params=self.query_params,
            headers=self.headers,
            body=self.request_body
        )


class AmazonAdsBaseRequestBuilder(AmazonAdsRequestBuilder):
    def __init__(self, resource: str) -> None:
        self._resource: str = resource
        self._client_access_token: str = None
        self._client_id: str = None
        self._profile_id: str = None

    @property
    def url(self) -> str:
        return f"{BASE_URL}/{self._resource}"

    @property
    def headers(self):
        return (super().headers or {}) | {
            "Amazon-Advertising-API-ClientId": self._client_id,
            "Amazon-Advertising-API-Scope": self._profile_id,
            "Authorization": f"Bearer {self._client_access_token}",
        }

    def with_client_access_token(self, client_access_token: str) -> "AmazonAdsBaseRequestBuilder":
        self._client_access_token: str = client_access_token
        return self

    def with_client_id(self, client_id: str) -> "AmazonAdsBaseRequestBuilder":
        self._client_id: str = client_id
        return self

    def with_profile_id(self, profile_id: str) -> "AmazonAdsBaseRequestBuilder":
        self._profile_id: str = str(profile_id)
        return self
