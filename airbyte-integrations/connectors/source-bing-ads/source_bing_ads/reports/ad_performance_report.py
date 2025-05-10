#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from abc import ABC

from .bing_ads_reporting_service_performance_stream import BingAdsReportingServicePerformanceStream
from .hourly_report_transformer_mixin import HourlyReportTransformerMixin


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
