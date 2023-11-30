#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Dict, List, Optional

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
    campaignId: Decimal
    name: str
    tags: Dict[str, str]
    budget: Decimal
    budgetType: str
    startDate: str
    endDate: str
    state: str
    servingStatus: str
    brandEntityId: str
    portfolioId: int
    bidOptimization: bool = None
    bidMultiplier: Decimal = None
    adFormat: str
    bidAdjustments: Optional[List[BidAdjustment]]
    creative: Optional[Creative]
    landingPage: Optional[LandingPage]
    supplySource: Optional[str]


class BrandsAdGroup(CatalogModel):
    campaignId: Decimal
    adGroupId: Decimal
    name: str
    bid: int
    keywordId: Decimal
    keywordText: str
    nativeLanguageKeyword: str
    matchType: str
    state: str
