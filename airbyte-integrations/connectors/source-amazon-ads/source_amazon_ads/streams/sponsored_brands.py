#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_amazon_ads.schemas import BrandsAdGroup, BrandsCampaign
from source_amazon_ads.streams.common import SubProfilesStream


class SponsoredBrandsCampaigns(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Brands Campaigns
    https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Campaigns
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_filter = kwargs.get("config", {}).get("state_filter")

    primary_key = "campaignId"
    state_filter = None
    model = BrandsCampaign

    def path(self, **kvargs) -> str:
        return "sb/campaigns"

    def request_params(self, *args, **kwargs):
        params = super().request_params(*args, **kwargs)
        if self.state_filter:
            params["stateFilter"] = ",".join(self.state_filter)
        return params


class SponsoredBrandsAdGroups(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Brands Ad groups
    https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Ad%20groups
    """

    primary_key = "adGroupId"
    model = BrandsAdGroup

    def path(self, **kvargs) -> str:
        return "sb/adGroups"


class SponsoredBrandsKeywords(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Brands Keywords
    https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Keywords
    """

    primary_key = "adGroupId"
    model = BrandsAdGroup

    def path(self, **kvargs) -> str:
        return "sb/keywords"
