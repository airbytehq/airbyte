#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
import xml.etree.ElementTree as ET
from abc import ABC
from typing import Any, List, Mapping, Tuple, Union
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
