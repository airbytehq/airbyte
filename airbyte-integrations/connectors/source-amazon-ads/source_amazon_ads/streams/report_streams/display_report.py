#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from enum import Enum

from .report_streams import RecordType, ReportStream

METRICS_MAP = {
    "campaigns": [
        "campaignName",
        "campaignId",
        "impressions",
        "clicks",
        "cost",
        "currency",
        "attributedConversions1d",
        "attributedConversions7d",
        "attributedConversions14d",
        "attributedConversions30d",
        "attributedConversions1dSameSKU",
        "attributedConversions7dSameSKU",
        "attributedConversions14dSameSKU",
        "attributedConversions30dSameSKU",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedSales1d",
        "attributedSales7d",
        "attributedSales14d",
        "attributedSales30d",
        "attributedSales1dSameSKU",
        "attributedSales7dSameSKU",
        "attributedSales14dSameSKU",
        "attributedSales30dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedUnitsOrderedNewToBrand14d",
    ],
    "adGroups": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "impressions",
        "clicks",
        "cost",
        "currency",
        "attributedConversions1d",
        "attributedConversions7d",
        "attributedConversions14d",
        "attributedConversions30d",
        "attributedConversions1dSameSKU",
        "attributedConversions7dSameSKU",
        "attributedConversions14dSameSKU",
        "attributedConversions30dSameSKU",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedSales1d",
        "attributedSales7d",
        "attributedSales14d",
        "attributedSales30d",
        "attributedSales1dSameSKU",
        "attributedSales7dSameSKU",
        "attributedSales14dSameSKU",
        "attributedSales30dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedUnitsOrderedNewToBrand14d",
    ],
    "productAds": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "asin",
        "sku",
        "adId",
        "impressions",
        "clicks",
        "cost",
        "currency",
        "attributedConversions1d",
        "attributedConversions7d",
        "attributedConversions14d",
        "attributedConversions30d",
        "attributedConversions1dSameSKU",
        "attributedConversions7dSameSKU",
        "attributedConversions14dSameSKU",
        "attributedConversions30dSameSKU",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedSales1d",
        "attributedSales7d",
        "attributedSales14d",
        "attributedSales30d",
        "attributedSales1dSameSKU",
        "attributedSales7dSameSKU",
        "attributedSales14dSameSKU",
        "attributedSales30dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedUnitsOrderedNewToBrand14d",
    ],
    "targets": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "targetId",
        "targetingExpression",
        "targetingText",
        "targetingType",
        "impressions",
        "clicks",
        "cost",
        "currency",
        "attributedConversions1d",
        "attributedConversions7d",
        "attributedConversions14d",
        "attributedConversions30d",
        "attributedConversions1dSameSKU",
        "attributedConversions7dSameSKU",
        "attributedConversions14dSameSKU",
        "attributedConversions30dSameSKU",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedSales1d",
        "attributedSales7d",
        "attributedSales14d",
        "attributedSales30d",
        "attributedSales1dSameSKU",
        "attributedSales7dSameSKU",
        "attributedSales14dSameSKU",
        "attributedSales30dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedUnitsOrderedNewToBrand14d",
    ],
    "asins": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "asin",
        "otherAsin",
        "sku",
        "currency",
        "attributedUnitsOrdered1dOtherSKU",
        "attributedUnitsOrdered7dOtherSKU",
        "attributedUnitsOrdered14dOtherSKU",
        "attributedUnitsOrdered30dOtherSKU",
        "attributedSales1dOtherSKU",
        "attributedSales7dOtherSKU",
        "attributedSales14dOtherSKU",
        "attributedSales30dOtherSKU",
    ],
}


class Tactics(str, Enum):
    T00001 = "T00001"
    T00020 = "T00020"
    T00030 = "T00030"
    REMARKETING = "remarketing"


class SponsoredDisplayReportStream(ReportStream):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Reports
    """

    def report_init_endpoint(self, record_type: str) -> str:
        return f"/sd/{record_type}/report"

    metrics_map = METRICS_MAP

    def _get_init_report_body(self, report_date: str, record_type: str, profile):
        if record_type == RecordType.ASINS and profile.accountInfo.type == "vendor":
            return None
        return {
            "reportDate": report_date,
            # Only for most common T00020 tactic for now
            "tactic": Tactics.T00020,
            "metrics": ",".join(self.metrics_map[record_type]),
        }
