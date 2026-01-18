#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS, HttpRequest

from .config import (
    AD_ACCOUNT_ID,
    AD_ID,
    ADSQUAD_ID,
    CAMPAIGN_ID,
    ORGANIZATION_ID,
)


SNAPCHAT_API_URL = "https://adsapi.snapchat.com/v1"
OAUTH_TOKEN_URL = "https://accounts.snapchat.com/login/oauth2/access_token"


class OAuthRequestBuilder:
    @classmethod
    def oauth_endpoint(
        cls,
        client_id: str = "test_client_id",
        client_secret: str = "test_client_secret",
        refresh_token: str = "test_refresh_token",
    ) -> "OAuthRequestBuilder":
        return cls(client_id, client_secret, refresh_token)

    def __init__(
        self,
        client_id: str = "test_client_id",
        client_secret: str = "test_client_secret",
        refresh_token: str = "test_refresh_token",
    ) -> None:
        self._body = f"grant_type=refresh_token&client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}"

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=OAUTH_TOKEN_URL,
            body=self._body,
        )


class RequestBuilder:
    @classmethod
    def organizations_endpoint(cls, organization_id: str = "me") -> "RequestBuilder":
        if organization_id == "me":
            return cls(resource="me/organizations")
        return cls(resource=f"organizations/{organization_id}")

    @classmethod
    def adaccounts_endpoint(cls, organization_id: str = ORGANIZATION_ID) -> "RequestBuilder":
        return cls(resource=f"organizations/{organization_id}/adaccounts")

    @classmethod
    def adaccounts_by_id_endpoint(cls, ad_account_id: str = AD_ACCOUNT_ID) -> "RequestBuilder":
        return cls(resource=f"adaccounts/{ad_account_id}")

    @classmethod
    def creatives_endpoint(cls, ad_account_id: str = AD_ACCOUNT_ID) -> "RequestBuilder":
        return cls(resource=f"adaccounts/{ad_account_id}/creatives")

    @classmethod
    def ads_endpoint(cls, ad_account_id: str = AD_ACCOUNT_ID) -> "RequestBuilder":
        return cls(resource=f"adaccounts/{ad_account_id}/ads")

    @classmethod
    def adsquads_endpoint(cls, ad_account_id: str = AD_ACCOUNT_ID) -> "RequestBuilder":
        return cls(resource=f"adaccounts/{ad_account_id}/adsquads")

    @classmethod
    def segments_endpoint(cls, ad_account_id: str = AD_ACCOUNT_ID) -> "RequestBuilder":
        return cls(resource=f"adaccounts/{ad_account_id}/segments")

    @classmethod
    def media_endpoint(cls, ad_account_id: str = AD_ACCOUNT_ID) -> "RequestBuilder":
        return cls(resource=f"adaccounts/{ad_account_id}/media")

    @classmethod
    def campaigns_endpoint(cls, ad_account_id: str = AD_ACCOUNT_ID) -> "RequestBuilder":
        return cls(resource=f"adaccounts/{ad_account_id}/campaigns")

    @classmethod
    def adaccounts_stats_endpoint(cls, ad_account_id: str = AD_ACCOUNT_ID) -> "RequestBuilder":
        return cls(resource=f"adaccounts/{ad_account_id}/stats")

    @classmethod
    def ads_stats_endpoint(cls, ad_id: str = AD_ID) -> "RequestBuilder":
        return cls(resource=f"ads/{ad_id}/stats")

    @classmethod
    def adsquads_stats_endpoint(cls, adsquad_id: str = ADSQUAD_ID) -> "RequestBuilder":
        return cls(resource=f"adsquads/{adsquad_id}/stats")

    @classmethod
    def campaigns_stats_endpoint(cls, campaign_id: str = CAMPAIGN_ID) -> "RequestBuilder":
        return cls(resource=f"campaigns/{campaign_id}/stats")

    def __init__(self, resource: str = "") -> None:
        self._resource = resource
        self._query_params: Dict[str, Any] = {}
        self._body = None

    def with_query_param(self, key: str, value: Any) -> "RequestBuilder":
        self._query_params[key] = value
        return self

    def with_granularity(self, granularity: str) -> "RequestBuilder":
        self._query_params["granularity"] = granularity
        return self

    def with_fields(self, fields: str) -> "RequestBuilder":
        self._query_params["fields"] = fields
        return self

    def with_start_time(self, start_time: str) -> "RequestBuilder":
        self._query_params["start_time"] = start_time
        return self

    def with_end_time(self, end_time: str) -> "RequestBuilder":
        self._query_params["end_time"] = end_time
        return self

    def with_action_report_time(self, action_report_time: str) -> "RequestBuilder":
        self._query_params["action_report_time"] = action_report_time
        return self

    def with_view_attribution_window(self, window: str) -> "RequestBuilder":
        self._query_params["view_attribution_window"] = window
        return self

    def with_swipe_up_attribution_window(self, window: str) -> "RequestBuilder":
        self._query_params["swipe_up_attribution_window"] = window
        return self

    def with_any_query_params(self) -> "RequestBuilder":
        self._any_query_params = True
        return self

    def build(self) -> HttpRequest:
        query_params = (
            ANY_QUERY_PARAMS if getattr(self, "_any_query_params", False) else (self._query_params if self._query_params else None)
        )
        return HttpRequest(
            url=f"{SNAPCHAT_API_URL}/{self._resource}",
            query_params=query_params,
            body=self._body,
        )
