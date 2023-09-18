#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from .common import CatalogModel
from typing import Optional


class AttributionReportModel(CatalogModel):
    date: str
    brandName: str
    marketplace: str
    campaignId: Optional[str]
    productAsin: str
    productConversionType: str
    advertiserName: str
    adGroupId: Optional[str]
    creativeId: Optional[str]
    productName: str
    productCategory: str
    productSubcategory: str
    productGroup: str
    publisher: Optional[str]
