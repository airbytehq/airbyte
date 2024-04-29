#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone


def transform_bulk_datetime_format_to_rfc_3339(original_value: str) -> str:
    """
    Bing Ads Bulk API provides datetime fields in custom format with milliseconds: "04/27/2023 18:00:14.970"
    Return datetime in RFC3339 format: "2023-04-27T18:00:14.970+00:00"
    """
    return datetime.strptime(original_value, "%m/%d/%Y %H:%M:%S.%f").replace(tzinfo=timezone.utc).isoformat(timespec="milliseconds")


def transform_date_format_to_rfc_3339(original_value: str) -> str:
    """
    Bing Ads API provides date fields in custom format: "04/27/2023"
    Return date in RFC3339 format: "2023-04-27"
    """
    return datetime.strptime(original_value, "%m/%d/%Y").replace(tzinfo=timezone.utc).strftime("%Y-%m-%d")


def transform_report_hourly_datetime_format_to_rfc_3339(original_value: str) -> str:
    """
    Bing Ads API reports with hourly aggregation provides date fields in custom format: "2023-11-04|11"
    Return date in RFC3339 format: "2023-11-04T11:00:00+00:00"
    """
    return datetime.strptime(original_value, "%Y-%m-%d|%H").replace(tzinfo=timezone.utc).isoformat(timespec="seconds")
