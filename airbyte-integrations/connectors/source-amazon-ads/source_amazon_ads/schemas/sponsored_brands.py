#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Dict, Optional

from .common import CatalogModel


class BrandsCampaign(CatalogModel):
    campaignId: int
    name: Optional[str]
    tags: Optional[Dict[str, str]]
    budget: Optional[Decimal]
    budgetType: Optional[str]
    startDate: Optional[str]
    endDate: Optional[str]
    state: Optional[str]
    servingStatus: Optional[str]
    brandEntityId: Optional[str]
    portfolioId: Optional[Decimal]
    bidOptimization: Optional[bool] = None
    bidMultiplier: Optional[Decimal] = None
    adFormat: Optional[str]


class BrandsAdGroup(CatalogModel):
    campaignId: Optional[int]
    adGroupId: int
    name: Optional[str]
