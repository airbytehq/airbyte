#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from .report_streams import ReportStream

METRICS_MAP = {
    "keywords": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",
        "adGroupName",
        "adGroupId",
        "keywordText",
        "keywordBid",
        "keywordStatus",
        "matchType",
        "impressions",
        "clicks",
        "cost",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedBrandedSearches14d",
        "attributedDetailPageViewsClicks14d",
        "attributedOrderRateNewToBrand14d",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "dpv14d",
        "keywordId",
        "vctr",
        "video5SecondViewRate",
        "video5SecondViews",
        "videoCompleteViews",
        "videoFirstQuartileViews",
        "videoMidpointViews",
        "videoThirdQuartileViews",
        "videoUnmutes",
        "viewableImpressions",
        "vtr",
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
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "vctr",
        "video5SecondViewRate",
        "video5SecondViews",
        "videoCompleteViews",
        "videoFirstQuartileViews",
        "videoMidpointViews",
        "videoThirdQuartileViews",
        "videoUnmutes",
        "viewableImpressions",
        "vtr",
        "dpv14d",
        "attributedDetailPageViewsClicks14d",
        "attributedOrderRateNewToBrand14d",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "attributedBrandedSearches14d",
    ],
    "campaigns": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",
        "impressions",
        "clicks",
        "cost",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "attributedBrandedSearches14d",
        "attributedDetailPageViewsClicks14d",
        "attributedOrderRateNewToBrand14d",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "dpv14d",
        "vctr",
        "video5SecondViewRate",
        "video5SecondViews",
        "videoCompleteViews",
        "videoFirstQuartileViews",
        "videoMidpointViews",
        "videoThirdQuartileViews",
        "videoUnmutes",
        "viewableImpressions",
        "vtr",
    ],
}


METRICS_TYPE_TO_ID_MAP = {
    "keywords": "keywordBid",
    "adGroups": "adGroupId",
    "campaigns": "campaignId",
}


class SponsoredBrandsVideoReportStream(ReportStream):
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
            "creativeType": "video",
        }
        yield {**body, "metrics": ",".join(metrics_list)}
