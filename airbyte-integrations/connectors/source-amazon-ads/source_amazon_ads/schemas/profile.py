#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal

from .common import CatalogModel


class AccountInfo(CatalogModel):
    marketplaceStringId: str
    id: str
    type: str
    name: str = None
    subType: str = None
    validPaymentMethod: bool = None


class Profile(CatalogModel):
    profileId: int
    countryCode: str = None
    currencyCode: str = None
    dailyBudget: Decimal = None
    timezone: str
    accountInfo: AccountInfo
