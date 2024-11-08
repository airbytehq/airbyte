#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC
from http import HTTPStatus
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from requests import Response
from source_amazon_ads.streams.common import SubProfilesStream

LOGGER = logging.getLogger("airbyte")


class SponsoredProductsV3(SubProfilesStream):
    """
    This Stream supports the Sponsored Products v3 API, which requires POST methods
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod
    """

    @property
    def http_method(self, **kwargs) -> str:
        return "POST"

    def request_headers(self, profile_id: str = None, *args, **kwargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kwargs)
        headers["Accept"] = self.content_type
        headers["Content-Type"] = self.content_type
        return headers

    def next_page_token(self, response: Response) -> str:
        if not response:
            return None
        return response.json().get("nextToken", None)

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        request_body = {}
        request_body["maxResults"] = self.page_size
        if next_page_token:
            request_body["nextToken"] = next_page_token
        return request_body

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: int = None,
    ) -> MutableMapping[str, Any]:
        return {}


class SponsoredProductCampaigns(SponsoredProductsV3):
    """
    This stream corresponds to Amazon Ads API - Sponsored Products (v3) Campaigns
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Campaigns/operation/ListSponsoredProductsCampaigns
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_filter = kwargs.get("config", {}).get("state_filter")

    primary_key = "campaignId"
    data_field = "campaigns"
    state_filter = None
    content_type = "application/vnd.spCampaign.v3+json"

    def path(self, **kwargs) -> str:
        return "sp/campaigns/list"

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        request_body = super().request_body_json(stream_state, stream_slice, next_page_token)
        if self.state_filter:
            request_body["stateFilter"] = {"include": self.state_filter}
        return request_body


class SponsoredProductAdGroups(SponsoredProductsV3):
    """
    This stream corresponds to Amazon Ads API - Sponsored Products (v3) Ad groups
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Ad-groups/operation/ListSponsoredProductsAdGroups
    """

    primary_key = "adGroupId"
    data_field = "adGroups"
    content_type = "application/vnd.spAdGroup.v3+json"

    def path(self, **kwargs) -> str:
        return "/sp/adGroups/list"


class SponsoredProductAdGroupWithSlicesABC(SponsoredProductsV3, ABC):
    """ABC Class for extraction of additional information for each known sp ad group"""

    primary_key = "adGroupId"

    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs
        super().__init__(*args, **kwargs)

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from SponsoredProductAdGroups(*self.__args, **self.__kwargs).read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=None, stream_state=stream_state
        )

    def parse_response(self, response: Response, **kwargs) -> Iterable[Mapping]:

        resp = response.json()
        if response.status_code == HTTPStatus.OK:
            yield resp

    def get_error_handler(self) -> ErrorHandler:
        error_mapping = DEFAULT_ERROR_MAPPING | {
            400: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message="Skip current AdGroup because it does not support request {response.request.url} for current profile",
            ),
            422: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message="Skip current AdGroup because the ad group {json.loads(response.request.body)['adGroupId']} does not have any asins",
            ),
            404: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message="Skip current AdGroup because the specified ad group has no associated bid",
            ),
        }
        return HttpStatusErrorHandler(logger=LOGGER, error_mapping=error_mapping)


class SponsoredProductAdGroupBidRecommendations(SponsoredProductAdGroupWithSlicesABC):
    """
    This stream corresponds to Amazon Ads API - Sponsored Products (v3) Ad group bid recommendations, now referred to as "Target Bid Recommendations" by Amazon Ads
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#tag/Bid-Recommendations/operation/getTargetBidRecommendations
    """

    primary_key = None
    data_field = "bidRecommendations"
    content_type = "application/vnd.spthemebasedbidrecommendation.v4+json"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "/sp/targets/bid/recommendations"

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        self.current_ad_group_id = stream_slice["adGroupId"]
        self.current_campaign_id = stream_slice["campaignId"]

        request_body = {}
        request_body["targetingExpressions"] = [
            {"type": "CLOSE_MATCH"},
            {"type": "LOOSE_MATCH"},
            {"type": "SUBSTITUTES"},
            {"type": "COMPLEMENTS"},
        ]
        request_body["adGroupId"] = stream_slice["adGroupId"]
        request_body["campaignId"] = stream_slice["campaignId"]
        request_body["recommendationType"] = "BIDS_FOR_EXISTING_AD_GROUP"
        return request_body

    def parse_response(self, response: Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            record["adGroupId"] = self.current_ad_group_id
            record["campaignId"] = self.current_campaign_id
            yield record


class SponsoredProductAdGroupSuggestedKeywords(SponsoredProductAdGroupWithSlicesABC):
    """Docs:
    V2 API:
        https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Suggested%20keywords
        GET /v2/sp/adGroups/{{adGroupId}}>/suggested/keywords
    """

    primary_key = None
    data_field = ""

    @property
    def http_method(self, **kwargs) -> str:
        return "GET"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"v2/sp/adGroups/{stream_slice['adGroupId']}/suggested/keywords"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: int = None
    ) -> MutableMapping[str, Any]:
        return {"maxNumSuggestions": 100}

    def request_headers(self, profile_id: str = None, *args, **kwargs) -> MutableMapping[str, Any]:
        headers = {}
        headers["Amazon-Advertising-API-Scope"] = str(self._current_profile_id)
        headers["Amazon-Advertising-API-ClientId"] = self._client_id
        return headers

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {}


class SponsoredProductKeywords(SponsoredProductsV3):
    """
    This stream corresponds to Amazon Ads Sponsored Products v3 API - Sponsored Products Keywords
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Keywords/operation/ListSponsoredProductsKeywords
    """

    primary_key = "keywordId"
    data_field = "keywords"
    content_type = "application/vnd.spKeyword.v3+json"

    def path(self, **kwargs) -> str:
        return "sp/keywords/list"


class SponsoredProductNegativeKeywords(SponsoredProductsV3):
    """
    This stream corresponds to Amazon Ads Sponsored Products v3 API - Sponsored Products Negative Keywords
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Negative-keywords/operation/ListSponsoredProductsNegativeKeywords
    """

    primary_key = "keywordId"
    data_field = "negativeKeywords"
    content_type = "application/vnd.spNegativeKeyword.v3+json"

    def path(self, **kwargs) -> str:
        return "sp/negativeKeywords/list"


class SponsoredProductCampaignNegativeKeywords(SponsoredProductsV3):
    """
    This stream corresponds to Amazon Ads Sponsored Products v3 API - Sponsored Products Negative Keywords
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Campaign-negative-keywords/operation/ListSponsoredProductsCampaignNegativeKeywords
    """

    primary_key = "keywordId"
    data_field = "campaignNegativeKeywords"
    content_type = "application/vnd.spCampaignNegativeKeyword.v3+json"

    def path(self, **kwargs) -> str:
        return "sp/campaignNegativeKeywords/list"


class SponsoredProductAds(SponsoredProductsV3):
    """
    This stream corresponds to Amazon Ads v3 API - Sponsored Products Ads
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Product-ads/operation/ListSponsoredProductsProductAds
    """

    primary_key = "adId"
    data_field = "productAds"
    content_type = "application/vnd.spProductAd.v3+json"

    def path(self, **kwargs) -> str:
        return "sp/productAds/list"


class SponsoredProductTargetings(SponsoredProductsV3):
    """
    This stream corresponds to Amazon Ads Sponsored Products v3 API - Sponsored Products Targeting Clauses
    """

    primary_key = "targetId"
    data_field = "targetingClauses"
    content_type = "application/vnd.spTargetingClause.v3+json"

    def path(self, **kwargs) -> str:
        return "sp/targets/list"
