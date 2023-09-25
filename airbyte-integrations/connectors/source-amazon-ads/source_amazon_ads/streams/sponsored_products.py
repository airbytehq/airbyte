#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from http import HTTPStatus
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests as requests
from airbyte_protocol.models import SyncMode
from source_amazon_ads.schemas import (
    Keywords,
    NegativeKeywords,
    ProductAd,
    ProductAdGroupBidRecommendations,
    ProductAdGroups,
    ProductAdGroupSuggestedKeywords,
    ProductCampaign,
    ProductTargeting,
)
from source_amazon_ads.streams.common import AmazonAdsStream, SubProfilesStream


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

    def path(self, **kvargs) -> str:
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

    def path(self, **kvargs) -> str:
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

    def request_headers(self, *args, **kvargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kvargs)
        headers["Amazon-Advertising-API-Scope"] = str(kvargs["stream_slice"]["profileId"])
        return headers

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from SponsoredProductAdGroupsWithProfileId(*self.__args, **self.__kwargs).read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=None, stream_state=stream_state
        )

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

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

    def path(self, **kvargs) -> str:
        return "v2/sp/keywords"


class SponsoredProductNegativeKeywords(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Products Negative Keywords
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Negative%20keywords
    """

    primary_key = "keywordId"
    model = NegativeKeywords

    def path(self, **kvargs) -> str:
        return "v2/sp/negativeKeywords"


class SponsoredProductCampaignNegativeKeywords(SponsoredProductNegativeKeywords):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Products Negative Keywords
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Negative%20keywords
    """

    def path(self, **kvargs) -> str:
        return "v2/sp/campaignNegativeKeywords"


class SponsoredProductAds(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Products Ads
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20ads
    """

    primary_key = "adId"
    model = ProductAd

    def path(self, **kvargs) -> str:
        return "v2/sp/productAds"


class SponsoredProductTargetings(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Products Targetings
    https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20targeting
    """

    primary_key = "targetId"
    model = ProductTargeting

    def path(self, **kvargs) -> str:
        return "v2/sp/targets"
