#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
import xml.etree.ElementTree as ET
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple, Union
from urllib.parse import urlparse

from bingads.v13.internal.reporting.row_report import _RowReport
from suds import WebFault

from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_bing_ads.reports import BingAdsReportingServicePerformanceStream, BingAdsReportingServiceStream, HourlyReportTransformerMixin
from source_bing_ads.utils import transform_date_format_to_rfc_3339, transform_report_hourly_datetime_format_to_rfc_3339


class AccountPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "AccountPerformanceReport"
    report_schema_name = "account_performance_report"
    primary_key = [
        "AccountId",
        "TimePeriod",
        "CurrencyCode",
        "AdDistribution",
        "DeviceType",
        "Network",
        "DeliveredMatchType",
        "DeviceOS",
        "TopVsOther",
        "BidMatchType",
    ]


class AccountPerformanceReportHourly(HourlyReportTransformerMixin, AccountPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "account_performance_report_hourly"


class AccountPerformanceReportDaily(AccountPerformanceReport):
    report_aggregation = "Daily"


class AccountPerformanceReportWeekly(AccountPerformanceReport):
    report_aggregation = "Weekly"


class AccountPerformanceReportMonthly(AccountPerformanceReport):
    report_aggregation = "Monthly"


class SearchQueryPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    report_name: str = "SearchQueryPerformanceReport"
    report_schema_name = "search_query_performance_report"

    primary_key = [
        "SearchQuery",
        "Keyword",
        "TimePeriod",
        "AccountId",
        "CampaignId",
        "Language",
        "DeliveredMatchType",
        "DeviceType",
        "DeviceOS",
        "TopVsOther",
    ]


class SearchQueryPerformanceReportHourly(HourlyReportTransformerMixin, SearchQueryPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "search_query_performance_report_hourly"


class SearchQueryPerformanceReportDaily(SearchQueryPerformanceReport):
    report_aggregation = "Daily"


class SearchQueryPerformanceReportWeekly(SearchQueryPerformanceReport):
    report_aggregation = "Weekly"


class SearchQueryPerformanceReportMonthly(SearchQueryPerformanceReport):
    report_aggregation = "Monthly"


class ProductSearchQueryPerformanceReport(BingAdsReportingServicePerformanceStream, ABC):
    """
    https://learn.microsoft.com/en-us/advertising/reporting-service/productsearchqueryperformancereportrequest?view=bingads-13
    """

    report_name: str = "ProductSearchQueryPerformanceReport"
    report_schema_name = "product_search_query_performance_report"
    primary_key = [
        "AccountId",
        "TimePeriod",
        "CampaignId",
        "AdId",
        "AdGroupId",
        "SearchQuery",
        "DeviceType",
        "DeviceOS",
        "Language",
        "Network",
    ]


class ProductSearchQueryPerformanceReportHourly(HourlyReportTransformerMixin, ProductSearchQueryPerformanceReport):
    report_aggregation = "Hourly"
    report_schema_name = "product_search_query_performance_report_hourly"


class ProductSearchQueryPerformanceReportDaily(ProductSearchQueryPerformanceReport):
    report_aggregation = "Daily"


class ProductSearchQueryPerformanceReportWeekly(ProductSearchQueryPerformanceReport):
    report_aggregation = "Weekly"


class ProductSearchQueryPerformanceReportMonthly(ProductSearchQueryPerformanceReport):
    report_aggregation = "Monthly"
