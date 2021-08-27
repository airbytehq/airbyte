#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from source_amazon_ads.schemas import DisplayAdGroup, DisplayCampaign, DisplayProductAds, DisplayTargeting
from source_amazon_ads.streams.common import SubProfilesStream


class SponsoredDisplayCampaigns(SubProfilesStream):
    """
    This stream corresponds to Amazon Advertising API - Sponsored Displays Campaigns
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns
    """

    primary_key = "campaignId"
    model = DisplayCampaign

    def path(self, **kvargs) -> str:
        return "sd/campaigns"


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
