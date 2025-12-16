# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, Optional

from airbyte_cdk.test.mock_http.request import HttpRequest


class LinkedInAdsRequestBuilder:
    """Builder class for creating LinkedIn Ads API request matchers."""

    _BASE_URL = "https://api.linkedin.com/rest"

    def __init__(self, path: str):
        self._path = path
        self._query_params: Dict[str, Any] = {}
        self._headers: Dict[str, str] = {}

    @classmethod
    def accounts_endpoint(cls) -> "LinkedInAdsRequestBuilder":
        return cls("/adAccounts")

    @classmethod
    def account_users_endpoint(cls, account_id: int) -> "LinkedInAdsRequestBuilder":
        builder = cls("/adAccountUsers")
        builder._query_params["q"] = "accounts"
        builder._query_params["accounts"] = f"urn:li:sponsoredAccount:{account_id}"
        return builder

    @classmethod
    def campaigns_endpoint(cls, account_id: int) -> "LinkedInAdsRequestBuilder":
        return cls(f"/adAccounts/{account_id}/adCampaigns")

    @classmethod
    def campaign_groups_endpoint(cls, account_id: int) -> "LinkedInAdsRequestBuilder":
        return cls(f"/adAccounts/{account_id}/adCampaignGroups")

    @classmethod
    def creatives_endpoint(cls, account_id: int) -> "LinkedInAdsRequestBuilder":
        return cls(f"/adAccounts/{account_id}/creatives")

    @classmethod
    def conversions_endpoint(cls, account_id: int) -> "LinkedInAdsRequestBuilder":
        builder = cls("/conversions")
        builder._query_params["q"] = "account"
        builder._query_params["account"] = f"urn:li:sponsoredAccount:{account_id}"
        return builder

    @classmethod
    def lead_forms_endpoint(cls, account_id: int) -> "LinkedInAdsRequestBuilder":
        builder = cls("/leadForms")
        builder._query_params["q"] = "owner"
        builder._query_params["owner"] = f"urn:li:sponsoredAccount:{account_id}"
        return builder

    @classmethod
    def lead_form_responses_endpoint(
        cls, account_id: int
    ) -> "LinkedInAdsRequestBuilder":
        builder = cls("/leadFormResponses")
        builder._query_params["q"] = "owner"
        builder._query_params["owner"] = f"urn:li:sponsoredAccount:{account_id}"
        return builder

    @classmethod
    def ad_analytics_endpoint(cls) -> "LinkedInAdsRequestBuilder":
        return cls("/adAnalytics")

    def with_query_param(self, key: str, value: Any) -> "LinkedInAdsRequestBuilder":
        self._query_params[key] = value
        return self

    def with_page_token(self, page_token: str) -> "LinkedInAdsRequestBuilder":
        self._query_params["pageToken"] = page_token
        return self

    def with_page_size(self, page_size: int) -> "LinkedInAdsRequestBuilder":
        self._query_params["pageSize"] = str(page_size)
        return self

    def with_start(self, start: int) -> "LinkedInAdsRequestBuilder":
        self._query_params["start"] = str(start)
        return self

    def with_count(self, count: int) -> "LinkedInAdsRequestBuilder":
        self._query_params["count"] = str(count)
        return self

    def with_q(self, q: str) -> "LinkedInAdsRequestBuilder":
        self._query_params["q"] = q
        return self

    def with_search(self, search: str) -> "LinkedInAdsRequestBuilder":
        self._query_params["search"] = search
        return self

    def with_any_query_params(self) -> "LinkedInAdsRequestBuilder":
        from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS

        self._query_params = ANY_QUERY_PARAMS
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{self._BASE_URL}{self._path}",
            query_params=self._query_params if self._query_params else None,
            headers=self._headers if self._headers else None,
        )
