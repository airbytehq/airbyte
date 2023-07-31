#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
        "costType",
        "campaignBudget",
        "campaignStatus",
        "attributedBrandedSearches14d",
        "attributedDetailPageView14d",
        "viewAttributedBrandedSearches14d",
        "viewAttributedConversions14d",
        "viewAttributedDetailPageView14d",
        "viewAttributedOrdersNewToBrand14d",
        "viewAttributedSales14d",
        "viewAttributedSalesNewToBrand14d",
        "viewAttributedUnitsOrdered14d",
        "viewAttributedUnitsOrderedNewToBrand14d",
        "viewImpressions",
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
        "attributedUnitsOrderedNewToBrand14d",
        "attributedBrandedSearches14d",
        "attributedDetailPageView14d",
        "bidOptimization",
        "viewAttributedBrandedSearches14d",
        "viewAttributedConversions14d",
        "viewAttributedDetailPageView14d",
        "viewAttributedOrdersNewToBrand14d",
        "viewAttributedSales14d",
        "viewAttributedSalesNewToBrand14d",
        "viewAttributedUnitsOrdered14d",
        "viewAttributedUnitsOrderedNewToBrand14d",
        "viewImpressions",
    ],
    "productAds": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "asin",
        "sku",  # Available for seller accounts only.
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
        "attributedBrandedSearches14d",
        "attributedDetailPageView14d",
        "viewAttributedBrandedSearches14d",
        "viewAttributedConversions14d",
        "viewAttributedDetailPageView14d",
        "viewAttributedOrdersNewToBrand14d",
        "viewAttributedSales14d",
        "viewAttributedSalesNewToBrand14d",
        "viewAttributedUnitsOrdered14d",
        "viewAttributedUnitsOrderedNewToBrand14d",
        "viewImpressions",
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
        "attributedBrandedSearches14d",
        "attributedDetailPageView14d",
        "viewAttributedBrandedSearches14d",
        "viewAttributedConversions14d",
        "viewAttributedDetailPageView14d",
        "viewAttributedOrdersNewToBrand14d",
        "viewAttributedSales14d",
        "viewAttributedSalesNewToBrand14d",
        "viewAttributedUnitsOrdered14d",
        "viewAttributedUnitsOrderedNewToBrand14d",
        "viewImpressions",
    ],
    "asins": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "asin",
        "otherAsin",
        "sku",  # Available for seller accounts only.
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


METRICS_TYPE_TO_ID_MAP = {"campaigns": "campaignId", "adGroups": "adGroupId", "productAds": "adId", "targets": "targetId", "asins": "asin"}


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
    metrics_type_to_id_map = METRICS_TYPE_TO_ID_MAP

    def _get_init_report_body(self, report_date: str, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        if record_type == RecordType.ASINS and profile.accountInfo.type == "vendor":
            return None
        elif record_type == RecordType.PRODUCTADS and profile.accountInfo.type != "seller":
            # Remove SKU from metrics since it is only available for seller accounts in Product Ad report
            metrics_list = [m for m in metrics_list if m != "sku"]
        return {
            "reportDate": report_date,
            # Only for most common T00020 tactic for now
            "tactic": Tactics.T00020,
            "metrics": ",".join(metrics_list),
        }
