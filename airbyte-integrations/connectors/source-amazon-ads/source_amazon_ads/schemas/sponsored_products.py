#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Dict, List, Optional

from .common import CatalogModel, Targeting


class Adjustments(CatalogModel):
    predicate: Optional[str]
    percentage: Optional[Decimal]


class Bidding(CatalogModel):
    strategy: Optional[str]
    adjustments: Optional[List[Adjustments]]


class ProductCampaign(CatalogModel):
    portfolioId: int
    campaignId: int
    name: Optional[str]
    tags: Optional[Dict[str, str]]
    campaignType: Optional[str]
    targetingType: Optional[str]
    state: Optional[str]
    dailyBudget: Optional[Decimal]
    startDate: Optional[str]
    endDate: Optional[str] = None
    premiumBidAdjustment: Optional[bool]
    bidding: Optional[Bidding]


class ProductAdGroups(CatalogModel):
    adGroupId: int
    name: Optional[str]
    campaignId: int
    defaultBid: Optional[Decimal]
    state: Optional[str]


class ProductAd(CatalogModel):
    adId: int
    campaignId: int
    adGroupId: int
    sku: Optional[str]
    asin: Optional[str]
    state: Optional[str]


class ProductTargeting(Targeting):
    campaignId: int
