# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional

from .base_request_builder import AmazonAdsBaseRequestBuilder


class SponsoredBrandsRequestBuilder(AmazonAdsBaseRequestBuilder):
    @classmethod
    def ad_groups_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, limit: Optional[int] = 100, start_index: Optional[int] = 0
    ) -> "SponsoredBrandsRequestBuilder":
        return cls("sb/adGroups") \
            .with_client_id(client_id) \
            .with_client_access_token(client_access_token) \
            .with_profile_id(profile_id) \
            .with_limit(limit) \
            .with_start_index(start_index)

    @classmethod
    def keywords_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, limit: Optional[int] = 100, start_index: Optional[int] = 0
    ) -> "SponsoredBrandsRequestBuilder":
        return cls("sb/keywords") \
            .with_client_id(client_id) \
            .with_client_access_token(client_access_token) \
            .with_profile_id(profile_id) \
            .with_limit(limit) \
            .with_start_index(start_index)

    @classmethod
    def campaigns_endpoint(
        cls, client_id: str, client_access_token: str, profile_id: str, limit: Optional[int] = 100, start_index: Optional[int] = 0
    ) -> "SponsoredBrandsRequestBuilder":
        return cls("sb/campaigns") \
            .with_client_id(client_id) \
            .with_client_access_token(client_access_token) \
            .with_profile_id(profile_id) \
            .with_limit(limit) \
            .with_start_index(start_index)

    def __init__(self, resource: str) -> None:
        super().__init__(resource)
        self._limit: Optional[int] = None
        self._start_index: Optional[int] = None

    @property
    def query_params(self) -> Dict[str, Any]:
        query_params = {}
        if self._limit is not None:
            query_params["count"] = self._limit
        if self._start_index:
            query_params["startIndex"] = self._start_index
        return query_params

    @property
    def request_body(self) ->Optional[str]:
        return None

    def with_limit(self, limit: int) -> "SponsoredBrandsRequestBuilder":
        self._limit: int = limit
        return self

    def with_start_index(self, offset: int) -> "SponsoredBrandsRequestBuilder":
        self._start_index: int = offset
        return self
