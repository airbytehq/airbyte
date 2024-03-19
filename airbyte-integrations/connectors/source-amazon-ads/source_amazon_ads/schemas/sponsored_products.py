#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Dict, List, Optional, Any

from .common import CatalogModel, Targeting


class Adjustments(CatalogModel):
    predicate: str
    percentage: Decimal


class Bidding(CatalogModel):
    strategy: str
    adjustments: List[Adjustments]

class ProductCampaign(CatalogModel):
    portfolioId: str
    campaignId: str
    name: str
    tags: Dict[str, str]
    targetingType: str
    state: str
    dynamicBidding: dict
    startDate: str
    endDate: str
    budget: dict
    extendedData: dict

class ProductAdGroups(CatalogModel):
    adGroupId: str
    name: str
    campaignId: str
    defaultBid: Decimal
    state: str
    extendedData: dict

class BidRecommendations(CatalogModel):
    bidValues: List[dict[str, str]]
    targetingExpression: dict[str, str]

class ProductAdGroupBidRecommendations(CatalogModel):
    adGroupId: str
    campaignId: str
    theme: str
    bidRecommendationsForTargetingExpressions: List[BidRecommendations]

class SuggestedKeyword(CatalogModel):
    keywordText: str
    matchType: str

class ProductAdGroupSuggestedKeywords(CatalogModel):
    adGroupId: Decimal
    suggestedKeywords: List[SuggestedKeyword] = None

class ProductAd(CatalogModel):
    adId: str
    campaignId: str
    customText: str
    asin: str
    state: str
    sku: str
    adGroupId: str
    extendedData: dict

class ProductTargeting(CatalogModel):
    expression: list
    targetId: str
    resolvedExpression: list
    campaignId: str
    expressionType: str
    state: str
    bid: float
    adGroupId: str
    extendedData: dict
