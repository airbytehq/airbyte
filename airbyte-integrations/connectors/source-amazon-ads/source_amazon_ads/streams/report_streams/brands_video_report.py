#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

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
        "targetId",
        "targetingExpression",
        "targetingText",
        "targetingType",
        "matchType",
        "impressions",
        "clicks",
        "cost",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
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
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
    ],
}


class SponsoredBrandsVideoReportStream(ReportStream):
    """
    https://advertising.amazon.com/API/docs/en-us/reference/sponsored-brands/2/reports
    """

    def report_init_endpoint(self, record_type: str) -> str:
        return f"/v2/hsa/{record_type}/report"

    metrics_map = METRICS_MAP

    def _get_init_report_body(self, report_date: str, record_type: str, profile):
        metrics_list = self.metrics_map[record_type]
        body = {
            "reportDate": report_date,
            "creativeType": "video",
        }
        return {**body, "metrics": ",".join(metrics_list)}
