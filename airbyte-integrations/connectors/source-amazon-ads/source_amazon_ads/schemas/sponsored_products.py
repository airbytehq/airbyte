#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Dict, List

from .common import CatalogModel, Targeting


class Adjustments(CatalogModel):
    predicate: str
    percentage: Decimal


class Bidding(CatalogModel):
    strategy: str
    adjustments: List[Adjustments]


class ProductCampaign(CatalogModel):
    portfolioId: Decimal
    campaignId: int
    name: str
    tags: Dict[str, str]
    campaignType: str
    targetingType: str
    state: str
    dailyBudget: Decimal
    startDate: str
    endDate: str = None
    premiumBidAdjustment: bool
    bidding: Bidding


class ProductAdGroups(CatalogModel):
    adGroupId: int
    name: str
    campaignId: int
    defaultBid: Decimal
    state: str


class ProductAd(CatalogModel):
    adId: int
    campaignId: int
    adGroupId: int
    sku: str
    asin: str
    state: str


class ProductTargeting(Targeting):
    campaignId: int
