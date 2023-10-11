#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from .common import CatalogModel


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
