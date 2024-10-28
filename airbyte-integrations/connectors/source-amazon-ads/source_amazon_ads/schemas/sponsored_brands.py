#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Any, Dict, List, Optional

from .common import CatalogModel


class LandingPage(CatalogModel):
    pageType: str
    url: str


class BidAdjustment(CatalogModel):
    bidAdjustmentPredicate: str
    bidAdjustmentPercent: int


class Creative(CatalogModel):
    brandName: str
    brandLogoAssetID: str
    brandLogoUrl: str
    asins: List[str]
    shouldOptimizeAsins: bool


class BrandsCampaign(CatalogModel):
    campaignId: str
    name: str
    tags: Dict[str, str]
    budget: Decimal
    budgetType: str
    startDate: str
    endDate: str
    state: str
    brandEntityId: str
    portfolioId: str
    ruleBasedBudget: Optional[Dict[str, Any]]
    bidding: Optional[Dict[str, Any]]
    productLocation: Optional[str]
    costType: Optional[str]
    smartDefault: Optional[List[str]]
    extendedData: Optional[Dict[str, Any]]


class BrandsAdGroup(CatalogModel):
    campaignId: str
    adGroupId: str
    name: str
    state: str
    extendedData: Dict[str, Any]
