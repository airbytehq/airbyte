#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from source_amazon_ads.streams.common import SubProfilesStream


class SponsoredDisplayCampaigns(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Displays Campaigns
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_filter = kwargs.get("config", {}).get("state_filter")

    primary_key = "campaignId"
    state_filter = None

    def path(self, **kwargs) -> str:
        return "sd/campaigns"

    def request_params(self, *args, **kwargs):
        params = super().request_params(*args, **kwargs)
        if self.state_filter:
            params["stateFilter"] = ",".join(self.state_filter)
        return params


class SponsoredDisplayAdGroups(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Displays Ad groups
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Ad%20groups
    """

    primary_key = "adGroupId"

    def path(self, **kwargs) -> str:
        return "sd/adGroups"


class SponsoredDisplayProductAds(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Displays Product Ads
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Product%20ads
    """

    primary_key = "adId"

    def path(self, **kwargs) -> str:
        return "sd/productAds"


class SponsoredDisplayTargetings(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Displays Targetings
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Targeting
    """

    primary_key = "targetId"

    def path(self, **kwargs) -> str:
        return "sd/targets"


class SponsoredDisplayCreatives(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Displays Creatives
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Creatives/listCreatives
    """

    primary_key = "creativeId"

    def path(self, **kwargs) -> str:
        return "/sd/creatives"


class SponsoredDisplayBudgetRules(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Displays BudgetRules
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi/prod#/BudgetRules/GetSDBudgetRulesForAdvertiser

    Important: API docs contains incorrect endpoint path:
        sd/budgetRules - endpoint from API docs which always returns empty results
        sp/budgetRules - working endpoint
    """

    primary_key = "ruleId"
    data_field = "budgetRulesForAdvertiserResponse"
    page_size = 30

    def path(self, **kwargs) -> str:
        return "sp/budgetRules"

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)
        params["pageSize"] = params.pop("count")
        return params
