#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from http import HTTPStatus
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from requests import Response
from airbyte_protocol.models import SyncMode
from source_amazon_ads.schemas import (
    Keywords,
    NegativeKeywords,
    ProductAd,
    ProductAdGroupBidRecommendations,
    ProductAdGroups,
    ProductAdGroupSuggestedKeywords,
    ProductCampaign,
    ProductCampaignV3,
    ProductTargeting,
)
from source_amazon_ads.streams.common import AmazonAdsStream, SubProfilesStream

class SponsoredProductCampaignsV3(SubProfilesStream):
    """
    This stream corresponds to Amazon Ads API - Sponsored Products Campaigns
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#tag/Campaigns/operation/ListSponsoredProductsCampaigns
    """

    primary_key = "campaignId"
    data_field = "campaigns"
    state_filter = None
    model = ProductCampaignV3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_filter = kwargs.get("config", {}).get("state_filter")

    def path(self, **kwargs) -> str:
        return "sp/campaigns/list"

    @property
    def http_method(self, **kwargs) -> str:
        return "POST"

    def request_headers(self, profile_id: str = None, *args, **kwargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kwargs)
        headers["Accept"] = "application/vnd.spCampaign.v3+json"
        headers["Content-Type"] = "application/vnd.spCampaign.v3+json"
        return headers

    def next_page_token(self, response: Response) -> str:
        if not response:
            return None
        return response.json().get("nextToken", None)

    def request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        request_body = {}
        if self.state_filter:
            request_body["stateFilter"] = {
                "include": self.state_filter
            }
        request_body["maxResults"] = self.page_size
        request_body["nextToken"] = next_page_token

        # tbd if included
        # request_body["campaignIdFilter"] = {
        #     "include": []
        # }
        # request_body["portfolioIdFilter"] = {
        #     "include": []
        # }
        # request_body["includeExtendedDataFields"] = True
        # request_body["nameFilter"] = {
        #     "queryTermMatchType": "EXACT_MATCH",
        #     "include": []
        # }

        return request_body

class SponsoredProductCampaigns(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Products Campaigns
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_filter = kwargs.get("config", {}).get("state_filter")

    primary_key = "campaignId"
    state_filter = None
    model = ProductCampaign

    def path(self, **kwargs) -> str:
        return "v2/sp/campaigns"

    def request_params(self, *args, **kwargs):
        params = super().request_params(*args, **kwargs)
        if self.state_filter:
            params["stateFilter"] = ",".join(self.state_filter)
        return params


class SponsoredProductAdGroups(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Products Ad groups
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Ad%20groups
    """

    primary_key = "adGroupId"
    model = ProductAdGroups

    def path(self, **kwargs) -> str:
        return "v2/sp/adGroups"


class SponsoredProductAdGroupsWithProfileId(SponsoredProductAdGroups):
    """Add profileId attr for each records in SponsoredProductAdGroups stream"""

    def parse_response(self, *args, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(*args, **kwargs):
            record["profileId"] = self._current_profile_id
            yield record


class SponsoredProductAdGroupWithSlicesABC(AmazonAdsStream, ABC):
    """ABC Class for extraction of additional information for each known sp ad group"""

    primary_key = "adGroupId"

    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs
        super().__init__(*args, **kwargs)

    def request_headers(self, *args, **kwargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kwargs)
        headers["Amazon-Advertising-API-Scope"] = str(kwargs["stream_slice"]["profileId"])
        return headers

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from SponsoredProductAdGroupsWithProfileId(*self.__args, **self.__kwargs).read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=None, stream_state=stream_state
        )

    def parse_response(self, response: Response, **kwargs) -> Iterable[Mapping]:

        resp = response.json()
        if response.status_code == HTTPStatus.OK:
            yield resp

        if response.status_code == HTTPStatus.BAD_REQUEST:
            # 400 error message for bids recommendation:
            #   Bid recommendation for AD group in Manual Targeted Campaign is not supported.
            # 400 error message for keywords recommendation:
            #   Getting keyword recommendations for AD Group in Auto Targeted Campaign is not supported
            self.logger.warning(
                f"Skip current AdGroup because it does not support request {response.request.url} for "
                f"{response.request.headers['Amazon-Advertising-API-Scope']} profile: {response.text}"
            )
        elif response.status_code == HTTPStatus.NOT_FOUND:
            # 404 Either the specified ad group identifier was not found,
            # or the specified ad group was found but no associated bid was found.
            self.logger.warning(
                f"Skip current AdGroup because the specified ad group has no associated bid {response.request.url} for "
                f"{response.request.headers['Amazon-Advertising-API-Scope']} profile: {response.text}"
            )

        else:
            response.raise_for_status()


class SponsoredProductAdGroupBidRecommendations(SponsoredProductAdGroupWithSlicesABC):
    """Docs:
    Latest API:
        https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Bid%20Recommendations/getTargetBidRecommendations
        POST /sd/targets/bid/recommendations
        Note: does not work, always get "403 Forbidden"

    V2 API:
        https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Bid%20recommendations/getAdGroupBidRecommendations
        GET /v2/sp/adGroups/{adGroupId}/bidRecommendations
    """

    model = ProductAdGroupBidRecommendations

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"v2/sp/adGroups/{stream_slice['adGroupId']}/bidRecommendations"


class SponsoredProductAdGroupSuggestedKeywords(SponsoredProductAdGroupWithSlicesABC):
    """Docs:
    Latest API:
        https://advertising.amazon.com/API/docs/en-us/sponsored-products/3-0/openapi/prod#/Keyword%20Targets/getRankedKeywordRecommendation
        POST /sp/targets/keywords/recommendations
        Note: does not work, always get "403 Forbidden"

    V2 API:
        https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Suggested%20keywords
        GET /v2/sp/adGroups/{{adGroupId}}>/suggested/keywords
    """

    model = ProductAdGroupSuggestedKeywords

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"v2/sp/adGroups/{stream_slice['adGroupId']}/suggested/keywords"


class SponsoredProductKeywords(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Products Keywords
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Keywords
    """

    primary_key = "keywordId"
    model = Keywords

    def path(self, **kwargs) -> str:
        return "v2/sp/keywords"


class SponsoredProductNegativeKeywords(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Products Negative Keywords
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Negative%20keywords
    """

    primary_key = "keywordId"
    model = NegativeKeywords

    def path(self, **kwargs) -> str:
        return "v2/sp/negativeKeywords"


class SponsoredProductCampaignNegativeKeywords(SponsoredProductNegativeKeywords):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Products Negative Keywords
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Negative%20keywords
    """

    def path(self, **kwargs) -> str:
        return "v2/sp/campaignNegativeKeywords"


class SponsoredProductAds(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Products Ads
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20ads
    """

    primary_key = "adId"
    model = ProductAd

    def path(self, **kwargs) -> str:
        return "v2/sp/productAds"


class SponsoredProductTargetings(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Products Targetings
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20targeting
    """

    primary_key = "targetId"
    model = ProductTargeting

    def path(self, **kwargs) -> str:
        return "v2/sp/targets"
