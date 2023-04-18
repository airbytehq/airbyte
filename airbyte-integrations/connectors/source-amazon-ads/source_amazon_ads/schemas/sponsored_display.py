#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Optional

from .common import CatalogModel, Targeting


class DisplayCampaign(CatalogModel):
    campaignId: int
    name: Optional[str]
    budgetType: Optional[str]
    budget: Optional[Decimal]
    startDate: Optional[str]
    endDate: Optional[str] = None
    costType: Optional[str]
    state: Optional[str]
    portfolioId: Optional[str] = None
    tactic: Optional[str]
    deliveryProfile: Optional[str]


class DisplayAdGroup(CatalogModel):
    name: Optional[str]
    campaignId: Optional[int]
    adGroupId: int
    defaultBid: Optional[Decimal]
    bidOptimization: Optional[str]
    state: Optional[str]
    tactic: Optional[str]


class DisplayProductAds(CatalogModel):
    state: Optional[str]
    adId: int
    campaignId: Optional[int]
    adGroupId: Optional[int]
    asin: Optional[str]
    sku: Optional[str]


class DisplayTargeting(Targeting):
    pass
