#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List

from .common import CatalogModel


class Report(CatalogModel):
    date: str
    brandName: str
    marketplace: str
    campaignId: str
    productAsin: str
    productConversionType: str
    advertiserName: str
    adGroupId: str
    creativeId: str
    productName: str
    productCategory: str
    productSubcategory: str
    productGroup: str
    publisher: str


class AttributionReportModel(CatalogModel):
    reports: List[Report]
    size: int
    cursorId: str
