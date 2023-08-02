#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Dict, List, Optional

from .common import CatalogModel, Targeting


class Adjustments(CatalogModel):
    predicate: str
    percentage: Decimal


class Bidding(CatalogModel):
    strategy: str
    adjustments: List[Adjustments]


class ProductCampaign(CatalogModel):
    portfolioId: int
    campaignId: Decimal
    name: str
    tags: Dict[str, str]
    campaignType: str
    targetingType: str
    state: str
    dailyBudget: Decimal
    ruleBasedBudget: Dict[str, str]
    startDate: str
    endDate: str = None
    premiumBidAdjustment: bool
    bidding: Bidding


class ProductAdGroups(CatalogModel):
    adGroupId: Decimal
    name: str
    campaignId: Decimal
    defaultBid: Decimal
    state: str


class SuggestedBid(CatalogModel):
    suggested: Decimal
    rangeStart: Decimal
    rangeEnd: Decimal


class ProductAdGroupBidRecommendations(CatalogModel):
    adGroupId: Decimal
    suggestedBid: Optional[SuggestedBid] = None


class SuggestedKeyword(CatalogModel):
    keywordText: str
    matchType: str


class ProductAdGroupSuggestedKeywords(CatalogModel):
    adGroupId: Decimal
    suggestedKeywords: List[SuggestedKeyword] = None


class ProductAd(CatalogModel):
    adId: Decimal
    campaignId: Decimal
    adGroupId: Decimal
    sku: str
    asin: str
    state: str


class ProductTargeting(Targeting):
    campaignId: Decimal
    expression: List[Dict[str, str]]
    resolvedExpression: List[Dict[str, str]]
