#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from .common import CatalogModel


class AttributionReportModel(CatalogModel):
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
