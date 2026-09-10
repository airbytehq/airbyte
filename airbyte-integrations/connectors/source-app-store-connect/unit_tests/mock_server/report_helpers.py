# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from http import HTTPStatus
from typing import Optional

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import error_response, tabular_response


@dataclass(frozen=True)
class ReportSpec:
    report_type: str
    report_subtype: Optional[str]
    version: Optional[str]
    start_date_config: str
    days_before_today: Optional[int] = None


REPORT_SPECS = {
    "subscriber_report": ReportSpec("SUBSCRIBER", "DETAILED", "1_3", "sales_reports_start_date", 2),
    "sales_report": ReportSpec("SALES", "SUMMARY", "1_0", "sales_reports_start_date", 2),
    "subscription_report": ReportSpec("SUBSCRIPTION", "SUMMARY", "1_3", "sales_reports_start_date", 2),
    "subscription_event_report": ReportSpec(
        "SUBSCRIPTION_EVENT",
        "SUMMARY",
        "1_3",
        "subscription_event_reports_start_date",
        3,
    ),
    "finance_report": ReportSpec("FINANCIAL", None, None, "finance_reports_start_date"),
}


def report_period(stream_name: str) -> str:
    spec = REPORT_SPECS[stream_name]
    today = datetime.now(timezone.utc).date()
    if stream_name == "finance_report":
        exclusive_end = (today - timedelta(days=35)).replace(day=1)
        return (exclusive_end - timedelta(days=1)).strftime("%Y-%m")
    return (today - timedelta(days=spec.days_before_today or 0)).isoformat()


def report_config(stream_name: str, start_period: Optional[str] = None) -> ConfigBuilder:
    period = start_period or report_period(stream_name)
    return ConfigBuilder().with_value(REPORT_SPECS[stream_name].start_date_config, period)


def previous_report_period(stream_name: str) -> str:
    period = report_period(stream_name)
    if stream_name == "finance_report":
        current = date.fromisoformat(f"{period}-01")
        return (current - timedelta(days=1)).strftime("%Y-%m")
    return (date.fromisoformat(period) - timedelta(days=1)).isoformat()


def report_state(stream_name: str, period: Optional[str] = None):
    cursor = period or report_period(stream_name)
    if stream_name == "finance_report":
        cursor = f"{cursor}-01"
    return StateBuilder().with_stream_state(stream_name, {"_sync_cursor": cursor}).build()


def next_report_cursor(stream_name: str, period: Optional[str] = None) -> str:
    period = period or report_period(stream_name)
    if stream_name == "finance_report":
        current = date.fromisoformat(f"{period}-01")
        return (current.replace(day=28) + timedelta(days=4)).replace(day=1).isoformat()
    return (date.fromisoformat(period) + timedelta(days=1)).isoformat()


def report_request(stream_name: str, period: Optional[str] = None) -> RequestBuilder:
    spec = REPORT_SPECS[stream_name]
    period = period or report_period(stream_name)
    if stream_name == "finance_report":
        return (
            RequestBuilder.finance_reports_endpoint()
            .with_query_param("filter[regionCode]", "ZZ")
            .with_query_param("filter[reportDate]", period)
            .with_query_param("filter[reportType]", spec.report_type)
            .with_query_param("filter[vendorNumber]", "12345678")
        )

    return (
        RequestBuilder.sales_reports_endpoint()
        .with_query_param("filter[version]", spec.version)
        .with_query_param("filter[frequency]", "DAILY")
        .with_query_param("filter[reportDate]", period)
        .with_query_param("filter[reportType]", spec.report_type)
        .with_query_param("filter[vendorNumber]", "12345678")
        .with_query_param("filter[reportSubType]", spec.report_subtype)
    )


def mock_report(
    http_mocker: HttpMocker,
    stream_name: str,
    response: Optional[HttpResponse] = None,
    period: Optional[str] = None,
) -> None:
    http_mocker.get(
        report_request(stream_name, period).build(),
        response or tabular_response(stream_name),
    )


def mock_missing_report(http_mocker: HttpMocker, stream_name: str) -> None:
    mock_report(http_mocker, stream_name, error_response(HTTPStatus.NOT_FOUND))
