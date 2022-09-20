#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal

from .common import CatalogModel, Targeting


class DisplayCampaign(CatalogModel):
    campaignId: int
    name: str
    budgetType: str
    budget: Decimal
    startDate: str
    endDate: str = None
    costType: str
    state: str
    portfolioId: str = None
    tactic: str
    deliveryProfile: str


class DisplayAdGroup(CatalogModel):
    name: str
    campaignId: int
    adGroupId: int
    defaultBid: Decimal
    bidOptimization: str
    state: str
    tactic: str


class DisplayProductAds(CatalogModel):
    state: str
    adId: int
    campaignId: int
    adGroupId: int
    asin: str
    sku: str


class DisplayTargeting(Targeting):
    pass
