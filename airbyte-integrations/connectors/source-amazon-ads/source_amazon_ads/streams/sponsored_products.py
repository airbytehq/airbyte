#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_amazon_ads.schemas import Keywords, NegativeKeywords, ProductAd, ProductAdGroups, ProductCampaign, ProductTargeting
from source_amazon_ads.streams.common import SubProfilesStream


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
