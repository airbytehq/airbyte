#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_amazon_ads.schemas import DisplayAdGroup, DisplayCampaign, DisplayProductAds, DisplayTargeting
from source_amazon_ads.streams.common import SubProfilesStream


class SponsoredDisplayCampaigns(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Displays Campaigns
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns
    """

    def __init__(self, *args, **kvargs):
        state = kvargs.get("config", {}).get("stateFilter")
        self.state_filter = ",".join(state) if state else ""
        # print(args, kvargs)
        # print("we are here!", end="\n\n\n\n\n")
        # print(self.state_filter)
        super().__init__(*args, **kvargs)

    primary_key = "campaignId"
    model = DisplayCampaign

    def path(self, **kvargs) -> str:
        params = f"?stateFilter={self.state_filter}" if self.state_filter else ""
        return f"sd/campaigns{params}"


class SponsoredDisplayAdGroups(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Displays Ad groups
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Ad%20groups
    """

    primary_key = "adGroupId"
    model = DisplayAdGroup

    def path(self, **kvargs) -> str:
        return "sd/adGroups"


class SponsoredDisplayProductAds(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Displays Product Ads
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Product%20ads
    """

    primary_key = "adId"
    model = DisplayProductAds

    def path(self, **kvargs) -> str:
        return "sd/productAds"


class SponsoredDisplayTargetings(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Displays Targetings
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Targeting
    """

    primary_key = "targetId"
    model = DisplayTargeting

    def path(self, **kvargs) -> str:
        return "sd/targets"
