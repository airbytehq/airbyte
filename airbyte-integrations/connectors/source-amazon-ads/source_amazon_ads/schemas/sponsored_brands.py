#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Dict

from .common import CatalogModel


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


class BrandsAdGroup(CatalogModel):
    campaignId: Decimal
    adGroupId: Decimal
    name: str
