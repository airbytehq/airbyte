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

# Needs to be updated
class ProductAdGroups(CatalogModel):
    adGroupId: Decimal
    name: str
    campaignId: Decimal
    defaultBid: Decimal
    state: str

# Needs to be updated
class SuggestedBid(CatalogModel):
    suggested: Decimal
    rangeStart: Decimal
    rangeEnd: Decimal

# Needs to be updated
class ProductAdGroupBidRecommendations(CatalogModel):
    adGroupId: Decimal
    suggestedBid: Optional[SuggestedBid] = None

# Needs to be updated
class SuggestedKeyword(CatalogModel):
    keywordText: str
    matchType: str

# Needs to be updated
class ProductAdGroupSuggestedKeywords(CatalogModel):
    adGroupId: Decimal
    suggestedKeywords: List[SuggestedKeyword] = None

# Needs to be updated
class ProductAd(CatalogModel):
    adId: Decimal
    campaignId: Decimal
    adGroupId: Decimal
    sku: str
    asin: str
    state: str

# Needs to be updated
class ProductTargeting(Targeting):
    campaignId: Decimal
    expression: List[Dict[str, str]]
    resolvedExpression: List[Dict[str, str]]
