#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Dict, List

from .common import CatalogModel, Targeting


class Adjustments(CatalogModel):
    source_name: str
    predicate: str
    percentage: Decimal


class Bidding(CatalogModel):
    source_name: str
    strategy: str
    adjustments: List[Adjustments]


class ProductCampaign(CatalogModel):
    source_name: str
    portfolioId: Decimal
    campaignId: Decimal
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
    source_name: str
    adGroupId: Decimal
    name: str
    campaignId: Decimal
    defaultBid: Decimal
    state: str


class ProductAd(CatalogModel):
    source_name: str
    adId: Decimal
    campaignId: Decimal
    adGroupId: Decimal
    sku: str
    asin: str
    state: str


class ProductTargeting(Targeting):
    source_name: str
    campaignId: Decimal
