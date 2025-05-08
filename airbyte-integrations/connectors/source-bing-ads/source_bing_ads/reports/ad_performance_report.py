from abc import ABC

from source_bing_ads.report_streams import BingAdsReportingServicePerformanceStream, HourlyReportTransformerMixin

class AdPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "AdPerformanceReport"

    report_schema_name = "ad_performance_report"
    primary_key = [
        "AccountId",
        "CampaignId",
        "AdGroupId",
        "AdId",
        "TimePeriod",
        "CurrencyCode",
        "AdDistribution",
        "DeviceType",
        "Language",
        "Network",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
        "DeliveredMatchType",
    ]


class AdPerformanceReportHourly(HourlyReportTransformerMixin, AdPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "ad_performance_report_hourly"


class AdPerformanceReportDaily(AdPerformanceReport):
    report_aggregation = "Daily"


class AdPerformanceReportWeekly(AdPerformanceReport):
    report_aggregation = "Weekly"


class AdPerformanceReportMonthly(AdPerformanceReport):
    report_aggregation = "Monthly"
