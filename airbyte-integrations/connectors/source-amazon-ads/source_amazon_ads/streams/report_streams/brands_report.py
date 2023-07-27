#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus

from .products_report import SponsoredProductsReportStream
from .report_streams import ReportStream

METRICS_MAP = {
    "keywords": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",
        "campaignRuleBasedBudget",
        "applicableBudgetRuleId",
        "applicableBudgetRuleName",
        "adGroupName",
        "adGroupId",
        "keywordText",
        "keywordBid",
        "keywordStatus",
        "searchTermImpressionRank",
        "matchType",
        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",
        "attributedBrandedSearches14d",
        "keywordId",
        "searchTermImpressionShare",
    ],
    "adGroups": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",
        "adGroupName",
        "adGroupId",
        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",
        "attributedBrandedSearches14d",
    ],
    "campaigns": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",
        "campaignRuleBasedBudget",
        "applicableBudgetRuleId",
        "applicableBudgetRuleName",
        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",
        "attributedBrandedSearches14d",
    ],
}

METRICS_TYPE_TO_ID_MAP = {
    "keywords": "keywordBid",
    "adGroups": "adGroupId",
    "campaigns": "campaignId",
}


class SponsoredBrandsReportStream(ReportStream):
    """
    https://advertising.amazon.com/API/docs/en-us/reference/sponsored-brands/2/reports
    """

    def report_init_endpoint(self, record_type: str) -> str:
        return f"/v2/hsa/{record_type}/report"

    metrics_map = METRICS_MAP
    metrics_type_to_id_map = METRICS_TYPE_TO_ID_MAP

    def _get_init_report_body(self, report_date: str, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        body = {
            "reportDate": report_date,
        }
        return {**body, "metrics": ",".join(metrics_list)}


METRICS_MAP_V3 = {
    "purchasedAsin": [
        "campaignBudgetCurrencyCode",
        "campaignName",
        "adGroupName",
        "attributionType",
        "purchasedAsin",
        "productName",
        "productCategory",
        "sales14d",
        "orders14d",
        "unitsSold14d",
        "newToBrandSales14d",
        "newToBrandPurchases14d",
        "newToBrandUnitsSold14d",
        "newToBrandSalesPercentage14d",
        "newToBrandPurchasesPercentage14d",
        "newToBrandUnitsSoldPercentage14d",
    ]
}

METRICS_TYPE_TO_ID_MAP_V3 = {
    "purchasedAsin": "purchasedAsin",
}


class SponsoredBrandsV3ReportStream(SponsoredProductsReportStream):
    """
    https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types#purchased-product-reports
    """

    API_VERSION = "reporting"  # v3
    REPORT_DATE_FORMAT = "YYYY-MM-DD"
    ad_product = "SPONSORED_BRANDS"
    report_is_created = HTTPStatus.OK
    metrics_map = METRICS_MAP_V3
    metrics_type_to_id_map = METRICS_TYPE_TO_ID_MAP_V3

    def _get_init_report_body(self, report_date: str, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]

        reportTypeId = "sbPurchasedProduct"
        group_by = ["purchasedAsin"]

        body = {
            "name": f"{record_type} report {report_date}",
            "startDate": report_date,
            "endDate": report_date,
            "configuration": {
                "adProduct": self.ad_product,
                "groupBy": group_by,
                "columns": metrics_list,
                "reportTypeId": reportTypeId,
                "filters": [],
                "timeUnit": "SUMMARY",
                "format": "GZIP_JSON",
            },
        }

        return body
