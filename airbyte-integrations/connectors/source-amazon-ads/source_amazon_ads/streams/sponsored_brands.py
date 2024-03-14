#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Mapping, Any, MutableMapping

from requests import Response

from source_amazon_ads.schemas import BrandsAdGroup, BrandsCampaign, BrandsCampaignV4
from source_amazon_ads.streams.common import SubProfilesStream

class SponsoredBrandsCampaignsV4(SubProfilesStream):
    """
    This stream corresponds to Amazon Ads API - Sponsored Brands Campaigns v4
    https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Campaigns/operation/ListSponsoredBrandsCampaigns
    """

    primary_key = "campaignId"
    data_field = "campaigns"
    state_filter = None
    model = BrandsCampaignV4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # state filter?
        self.state_filter = kwargs.get("config", {}).get("state_filter", None)

    def path(self, **kwargs) -> str:
        return "sb/v4/campaigns/list"

    @property
    def http_method(self, **kwargs) -> str:
        return "POST"

    def request_headers(self, profile_id: str = None, *args, **kwargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kwargs)
        headers["Accept"] = "application/vnd.sbcampaignresource.v4+json"
        headers["Content-Type"] = "application/vnd.sbcampaignresource.v4+json"
        return headers

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

    def next_page_token(self, response: Response) -> str:
        if not response:
            return None
        return response.json().get("nextToken", None)

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

    def path(self, **kwargs) -> str:
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

    def path(self, **kwargs) -> str:
        return "sb/adGroups"


class SponsoredBrandsKeywords(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Brands Keywords
    https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Keywords
    """

    primary_key = "adGroupId"
    model = BrandsAdGroup

    def path(self, **kwargs) -> str:
        return "sb/keywords"
