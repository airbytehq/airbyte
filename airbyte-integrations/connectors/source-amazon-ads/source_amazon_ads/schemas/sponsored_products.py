#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Any, Dict, List, Optional

from .common import CatalogModel, KeywordsBase


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
    dynamicBidding: Dict[str, Any]
    startDate: str
    endDate: str
    budget: Dict[str, Any]
    extendedData: Optional[Dict[str, Any]]


class ProductAdGroups(CatalogModel):
    adGroupId: str
    name: str
    campaignId: str
    defaultBid: Decimal
    state: str
    extendedData: dict


class BidRecommendations(CatalogModel):
    bidValues: List[Dict[str, str]]
    targetingExpression: Dict[str, str]


class ProductAdGroupBidRecommendations(CatalogModel):
    adGroupId: str
    campaignId: str
    theme: str
    bidRecommendationsForTargetingExpressions: List[BidRecommendations]


class SuggestedKeyword(CatalogModel):
    keywordText: str
    matchType: str


class ProductAdGroupSuggestedKeywords(CatalogModel):
    adGroupId: int
    suggestedKeywords: List[SuggestedKeyword] = None


class ProductAd(CatalogModel):
    adId: str
    campaignId: str
    customText: str
    asin: str
    state: str
    sku: str
    adGroupId: str
    extendedData: Optional[Dict[str, Any]]


class ProductTargeting(CatalogModel):
    expression: List[Dict[str, str]]
    targetId: str
    resolvedExpression: List[Dict[str, str]]
    campaignId: str
    expressionType: str
    state: str
    bid: float
    adGroupId: str
    extendedData: Optional[Dict[str, Any]]


class SponsoredProductCampaignNegativeKeywordsModel(KeywordsBase):
    keywordId: str
    campaignId: str
    state: str
    keywordText: str
    extendedData: Optional[Dict[str, Any]]


class SponsoredProductKeywordsModel(KeywordsBase):
    keywordId: str
    nativeLanguageLocale: str
    campaignId: str
    state: str
    adGroupId: str
    keywordText: str
    extendedData: Optional[Dict[str, Any]]


class SponsoredProductNegativeKeywordsModel(KeywordsBase):
    keywordId: str
    nativeLanguageLocale: str
    campaignId: str
    state: str
    adGroupId: str
    keywordText: str
    extendedData: Optional[Dict[str, Any]]
