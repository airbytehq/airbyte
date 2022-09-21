#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Optional

from .common import CatalogModel


class AccountInfo(CatalogModel):
    marketplaceStringId: Optional[str]
    id: str
    type: Optional[str]
    name: Optional[str] = None
    subType: Optional[str] = None
    validPaymentMethod: Optional[bool] = None


class Profile(CatalogModel):
    profileId: int
    countryCode: Optional[str] = None
    currencyCode: Optional[str] = None
    dailyBudget: Optional[Decimal] = None
    timezone: Optional[str]
    accountInfo: Optional[AccountInfo]
