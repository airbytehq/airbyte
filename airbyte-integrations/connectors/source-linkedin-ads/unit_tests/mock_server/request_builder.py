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
        self._query_params_in_url = False  # Flag to indicate query params are embedded in URL

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
        # The lead_forms endpoint has the owner embedded in the path with URL encoding
        # Path format: leadForms?owner=(sponsoredAccount:urn%3Ali%3AsponsoredAccount%3A{account_id})&q=owner&count=500
        # The %3A is URL-encoded colon (:)
        # Note: We include all query params in the path since HttpRequest doesn't allow both
        builder = cls(f"/leadForms?owner=(sponsoredAccount:urn%3Ali%3AsponsoredAccount%3A{account_id})&q=owner&count=500")
        builder._query_params_in_url = True
        return builder

    @classmethod
    def lead_form_responses_endpoint(cls, account_id: int) -> "LinkedInAdsRequestBuilder":
        # The lead_form_responses endpoint has the owner embedded in the path with URL encoding
        # Path format: leadFormResponses?owner=(sponsoredAccount:urn%3Ali%3AsponsoredAccount%3A{account_id})&leadType=(leadType:SPONSORED)&q=owner&count=500
        # Note: We include all query params in the path since HttpRequest doesn't allow both
        builder = cls(
            f"/leadFormResponses?owner=(sponsoredAccount:urn%3Ali%3AsponsoredAccount%3A{account_id})&leadType=(leadType:SPONSORED)&q=owner&count=500"
        )
        builder._query_params_in_url = True
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
        url = f"{self._BASE_URL}{self._path}"

        # If query params are already embedded in the URL, append any additional params to the URL
        if self._query_params_in_url:
            # Append additional query params (like 'start' for pagination) to the URL
            if self._query_params:
                for key, value in self._query_params.items():
                    url = f"{url}&{key}={value}"
            query_params = None
        else:
            query_params = self._query_params if self._query_params else None

        return HttpRequest(
            url=url,
            query_params=query_params,
            headers=self._headers if self._headers else None,
        )
