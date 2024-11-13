#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any, Mapping, MutableMapping

from requests import Response
from source_amazon_ads.streams.common import SubProfilesStream


class SponsoredBrandsV4(SubProfilesStream):
    """
    This Stream supports the Sponsored Brands V4 API, which requires POST methods
    https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod
    """

    @property
    def http_method(self, **kwargs) -> str:
        return "POST"

    def request_headers(self, profile_id: str = None, *args, **kwargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kwargs)
        headers["Accept"] = self.content_type
        headers["Content-Type"] = self.content_type
        return headers

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        request_body = {}
        request_body["maxResults"] = self.page_size
        if next_page_token:
            request_body["nextToken"] = next_page_token
        return request_body

    def next_page_token(self, response: Response) -> str:
        if not response:
            return None
        return response.json().get("nextToken", None)

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: int = None,
    ) -> MutableMapping[str, Any]:
        return {}


class SponsoredBrandsCampaigns(SponsoredBrandsV4):
    """
    This stream corresponds to Amazon Ads API - Sponsored Brands Campaigns v4
    https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Campaigns/operation/ListSponsoredBrandsCampaigns
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_filter = kwargs.get("config", {}).get("state_filter")

    primary_key = "campaignId"
    data_field = "campaigns"
    state_filter = None
    content_type = "application/vnd.sbcampaignresource.v4+json"

    def path(self, **kwargs) -> str:
        return "sb/v4/campaigns/list"

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        request_body = super().request_body_json(stream_state, stream_slice, next_page_token)
        if self.state_filter:
            request_body["stateFilter"] = {"include": self.state_filter}
        return request_body


class SponsoredBrandsAdGroups(SponsoredBrandsV4):
    """
    This stream corresponds to Amazon Ads API - Sponsored Brands Ad Groups v4
    https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi/prod#tag/Ad-groups/operation/ListSponsoredBrandsAdGroups
    """

    primary_key = "adGroupId"
    data_field = "adGroups"
    content_type = "application/vnd.sbadgroupresource.v4+json"

    def path(self, **kwargs) -> str:
        return "sb/v4/adGroups/list"


class SponsoredBrandsKeywords(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Brands Keywords
    https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Keywords
    """

    primary_key = "adGroupId"

    def path(self, **kwargs) -> str:
        return "sb/keywords"
