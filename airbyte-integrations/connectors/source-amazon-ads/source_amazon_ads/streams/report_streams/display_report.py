#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from typing import Any, List, Mapping

import requests

from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from source_amazon_ads.streams.report_streams.report_stream_models import ReportInfo
from source_amazon_ads.streams.report_streams.report_streams import ReportStream


METRICS_MAP_V3 = {
    "campaigns": [
        "addToCart",
        "addToCartClicks",
        "addToCartRate",
        "addToCartViews",
        "addToList",
        "addToListFromClicks",
        "addToListFromViews",
        "qualifiedBorrows",
        "qualifiedBorrowsFromClicks",
        "qualifiedBorrowsFromViews",
        "royaltyQualifiedBorrows",
        "royaltyQualifiedBorrowsFromClicks",
        "royaltyQualifiedBorrowsFromViews",
        "brandedSearches",
        "brandedSearchesClicks",
        "brandedSearchesViews",
        "brandedSearchRate",
        "campaignBudgetCurrencyCode",
        "campaignId",
        "campaignName",
        "clicks",
        "cost",
        "detailPageViews",
        "detailPageViewsClicks",
        "eCPAddToCart",
        "eCPBrandSearch",
        "endDate",
        "impressions",
        "impressionsViews",
        "leadFormOpens",
        "leads",
        "linkOuts",
        "newToBrandPurchases",
        "newToBrandPurchasesClicks",
        "newToBrandSalesClicks",
        "newToBrandUnitsSold",
        "newToBrandUnitsSoldClicks",
        "purchases",
        "purchasesClicks",
        "purchasesPromotedClicks",
        "sales",
        "salesClicks",
        "salesPromotedClicks",
        "startDate",
        "unitsSold",
        "unitsSoldClicks",
        "videoCompleteViews",
        "videoFirstQuartileViews",
        "videoMidpointViews",
        "videoThirdQuartileViews",
        "videoUnmutes",
        "viewabilityRate",
        "viewClickThroughRate",
    ]
    + [  # Group-by metrics
        "campaignBudgetAmount",
        "campaignStatus",
        "costType",
        "cumulativeReach",
        "impressionsFrequencyAverage",
        "newToBrandDetailPageViewClicks",
        "newToBrandDetailPageViewRate",
        "newToBrandDetailPageViews",
        "newToBrandDetailPageViewViews",
        "newToBrandECPDetailPageView",
        "newToBrandSales",
    ],  # 'date',
    "adGroups": [
        "addToCart",
        "addToCartClicks",
        "addToCartRate",
        "addToCartViews",
        "adGroupId",
        "adGroupName",
        "addToList",
        "addToListFromClicks",
        "addToListFromViews",
        "qualifiedBorrows",
        "qualifiedBorrowsFromClicks",
        "qualifiedBorrowsFromViews",
        "royaltyQualifiedBorrows",
        "royaltyQualifiedBorrowsFromClicks",
        "royaltyQualifiedBorrowsFromViews",
        "bidOptimization",
        "brandedSearches",
        "brandedSearchesClicks",
        "brandedSearchesViews",
        "brandedSearchRate",
        "campaignBudgetCurrencyCode",
        "campaignId",
        "campaignName",
        "clicks",
        "cost",
        "detailPageViews",
        "detailPageViewsClicks",
        "eCPAddToCart",
        "eCPBrandSearch",
        "endDate",
        "impressions",
        "impressionsViews",
        "leadFormOpens",
        "leads",
        "linkOuts",
        "newToBrandPurchases",
        "newToBrandPurchasesClicks",
        "newToBrandSales",
        "newToBrandSalesClicks",
        "newToBrandUnitsSold",
        "newToBrandUnitsSoldClicks",
        "purchases",
        "purchasesClicks",
        "purchasesPromotedClicks",
        "sales",
        "salesClicks",
        "salesPromotedClicks",
        "startDate",
        "unitsSold",
        "unitsSoldClicks",
        "videoCompleteViews",
        "videoFirstQuartileViews",
        "videoMidpointViews",
        "videoThirdQuartileViews",
        "videoUnmutes",
        "viewabilityRate",
        "viewClickThroughRate",
    ]
    + [  # Group-by metrics
        "cumulativeReach",
        "impressionsFrequencyAverage",
        "newToBrandDetailPageViewClicks",
        "newToBrandDetailPageViewRate",
        "newToBrandDetailPageViews",
        "newToBrandDetailPageViewViews",
        "newToBrandECPDetailPageView",
    ],  # 'date',
    "productAds": [
        "addToCart",
        "addToCartRate",
        "addToCartViews",
        "addToCartClicks",
        "adGroupId",
        "adGroupName",
        "adId",
        "addToList",
        "addToListFromClicks",
        "qualifiedBorrows",
        "royaltyQualifiedBorrows",
        "addToListFromViews",
        "qualifiedBorrowsFromClicks",
        "qualifiedBorrowsFromViews",
        "royaltyQualifiedBorrowsFromClicks",
        "royaltyQualifiedBorrowsFromViews",
        "bidOptimization",
        "brandedSearches",
        "brandedSearchesClicks",
        "brandedSearchesViews",
        "brandedSearchRate",
        "campaignBudgetCurrencyCode",
        "campaignId",
        "campaignName",
        "clicks",
        "cost",
        "cumulativeReach",
        "detailPageViews",
        "detailPageViewsClicks",
        "eCPAddToCart",
        "eCPBrandSearch",
        "endDate",
        "impressions",
        "impressionsFrequencyAverage",
        "impressionsViews",
        "leadFormOpens",
        "leads",
        "linkOuts",
        "newToBrandDetailPageViewClicks",
        "newToBrandDetailPageViewRate",
        "newToBrandDetailPageViews",
        "newToBrandDetailPageViewViews",
        "newToBrandECPDetailPageView",
        "newToBrandPurchases",
        "newToBrandPurchasesClicks",
        "newToBrandSales",
        "newToBrandSalesClicks",
        "newToBrandUnitsSold",
        "newToBrandUnitsSoldClicks",
        "promotedAsin",
        "promotedSku",
        "purchases",
        "purchasesClicks",
        "purchasesPromotedClicks",
        "sales",
        "salesClicks",
        "salesPromotedClicks",
        "startDate",
        "unitsSold",
        "unitsSoldClicks",
        "videoCompleteViews",
        "videoFirstQuartileViews",
        "videoMidpointViews",
        "videoThirdQuartileViews",
        "videoUnmutes",
        "viewabilityRate",
        "viewClickThroughRate",
    ],  # 'date',
    "targets": [
        "addToCart",
        "addToCartClicks",
        "addToCartRate",
        "addToCartViews",
        "adGroupId",
        "adGroupName",
        "addToList",
        "addToListFromClicks",
        "addToListFromViews",
        "qualifiedBorrows",
        "qualifiedBorrowsFromClicks",
        "qualifiedBorrowsFromViews",
        "royaltyQualifiedBorrows",
        "royaltyQualifiedBorrowsFromClicks",
        "royaltyQualifiedBorrowsFromViews",
        "brandedSearches",
        "brandedSearchesClicks",
        "brandedSearchesViews",
        "brandedSearchRate",
        "campaignBudgetCurrencyCode",
        "campaignId",
        "campaignName",
        "clicks",
        "cost",
        "detailPageViews",
        "detailPageViewsClicks",
        "eCPAddToCart",
        "eCPBrandSearch",
        "endDate",
        "impressions",
        "impressionsViews",
        "leadFormOpens",
        "leads",
        "linkOuts",
        "newToBrandPurchases",
        "newToBrandPurchasesClicks",
        "newToBrandSales",
        "newToBrandSalesClicks",
        "newToBrandUnitsSold",
        "newToBrandUnitsSoldClicks",
        "purchases",
        "purchasesClicks",
        "purchasesPromotedClicks",
        "sales",
        "salesClicks",
        "salesPromotedClicks",
        "startDate",
        "targetingExpression",
        "targetingId",
        "targetingText",
        "unitsSold",
        "unitsSoldClicks",
        "videoCompleteViews",
        "videoFirstQuartileViews",
        "videoMidpointViews",
        "videoThirdQuartileViews",
        "videoUnmutes",
        "viewabilityRate",
        "viewClickThroughRate",
    ],  # 'date',
    "asins": [
        "adGroupId",
        "adGroupName",
        "asinBrandHalo",
        "addToList",
        "addToListFromClicks",
        "qualifiedBorrowsFromClicks",
        "royaltyQualifiedBorrowsFromClicks",
        "addToListFromViews",
        "qualifiedBorrows",
        "qualifiedBorrowsFromViews",
        "royaltyQualifiedBorrows",
        "royaltyQualifiedBorrowsFromViews",
        "campaignBudgetCurrencyCode",
        "campaignId",
        "campaignName",
        "conversionsBrandHalo",
        "conversionsBrandHaloClicks",
        "endDate",
        "promotedAsin",
        "promotedSku",
        "salesBrandHalo",
        "salesBrandHaloClicks",
        "startDate",
        "unitsSoldBrandHalo",
        "unitsSoldBrandHaloClicks",
    ],
}


METRICS_TYPE_TO_ID_MAP = {"campaigns": "campaignId", "adGroups": "adGroupId", "productAds": "adId", "targets": "targetId", "asins": "asin"}


class SponsoredDisplayReportStream(ReportStream):
    """
    https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Reports
    """

    API_VERSION = "reporting"  # v3
    REPORT_DATE_FORMAT = "YYYY-MM-DD"
    ad_product = "SPONSORED_DISPLAY"
    report_is_created = HTTPStatus.OK
    metrics_map = METRICS_MAP_V3
    metrics_type_to_id_map = METRICS_TYPE_TO_ID_MAP

    def __init__(self, config: Mapping[str, Any], profiles: List[dict[str, Any]], authenticator: Oauth2Authenticator):
        super().__init__(config, profiles, authenticator)
        # using session without auth as API returns 400 bad request if Authorization header presents in request
        # X-Amz-Algorithm and X-Amz-Signature query params already present in the url, that is enough to make proper request
        self._report_download_session = requests.Session()

    def report_init_endpoint(self, record_type: str) -> str:
        return f"/{self.API_VERSION}/reports"

    def _download_report(self, report_info: ReportInfo, url: str) -> List[dict]:
        """
        Download and parse report result
        """
        return super()._download_report(None, url)

    def _get_init_report_body(self, report_date: str, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]

        reportTypeId = "sdCampaigns"  # SponsoredDisplayCampaigns
        group_by = ["campaign"]
        filters = []

        if record_type == "adGroups":
            reportTypeId = "sdAdGroup"
            group_by = ["adGroup"]

        elif record_type == "productAds":
            reportTypeId = "sdAdvertisedProduct"
            group_by = ["advertiser"]

        elif record_type == "asins":
            reportTypeId = "sdPurchasedProduct"
            group_by = ["asin"]

        elif record_type == "keywords" or record_type == "targets":
            group_by = ["targeting"]
            reportTypeId = "sdTargeting"

            if record_type == "keywords":
                filters = [{"field": "keywordType", "values": ["BROAD", "PHRASE", "EXACT"]}]

        body = {
            "name": f"{record_type} report {report_date}",
            "startDate": report_date,
            "endDate": report_date,
            "configuration": {
                "adProduct": self.ad_product,
                "groupBy": group_by,
                "columns": metrics_list,
                "reportTypeId": reportTypeId,
                "filters": filters,
                "timeUnit": "SUMMARY",
                "format": "GZIP_JSON",
            },
        }

        yield body
