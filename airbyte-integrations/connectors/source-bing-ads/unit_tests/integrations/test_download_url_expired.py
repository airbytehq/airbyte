# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
import json
from pathlib import Path

import pytest
from base_test import create_zip_from_csv
from client_builder import build_request, build_request_2, response_with_status
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import BULK_BASE_URL, RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


ACCOUNTS_SEARCH_BODY = b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
ACCOUNT_IMPRESSION_PERFORMANCE_REPORT_HOURLY_SUBMIT_BODY = b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AccountPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "AccountPerformanceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CurrencyCode", "AdDistribution", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "AveragePosition", "Conversions", "ConversionRate", "CostPerConversion", "LowQualityClicks", "LowQualityClicksPercent", "LowQualityImpressions", "LowQualityImpressionsPercent", "LowQualityConversions", "LowQualityConversionRate", "DeviceType", "PhoneImpressions", "PhoneCalls", "Ptr", "Network", "Assists", "Revenue", "ReturnOnAdSpend", "CostPerAssist", "RevenuePerConversion", "RevenuePerAssist", "AccountStatus", "LowQualityGeneralClicks", "LowQualitySophisticatedClicks", "TopImpressionRatePercent", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "ViewThroughConversions", "AverageCpm", "ConversionsQualified", "LowQualityConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue", "VideoViews", "ViewThroughRate", "AverageCPV", "VideoViewsAt25Percent", "VideoViewsAt50Percent", "VideoViewsAt75Percent", "CompletedVideoViews", "VideoCompletionRate", "TotalWatchTimeInMS", "AverageWatchTimePerVideoView", "AverageWatchTimePerImpression", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}'

AZURE_SAS_EXPIRED_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.</Message><AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [Mon, 06 May 2024 00:00:00 GMT] - Expiry [Mon, 06 May 2024 00:10:00 GMT] - Current [Mon, 06 May 2024 00:20:00 GMT]"
    "</AuthenticationErrorDetail></Error>"
)
AZURE_SAS_EXPIRED_RESPONSE = HttpResponse(
    AZURE_SAS_EXPIRED_BODY,
    403,
    {"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"},
)


def _mock_accounts(http_mocker: HttpMocker, config: dict) -> None:
    http_mocker.post(request=build_request(config), responses=response_with_status("oauth", 200))
    http_mocker.post(request=build_request_2(config), responses=response_with_status("oauth", 200))
    http_mocker.post(
        RequestBuilder(resource="User/Query", api="client_center").with_body('{"UserId": null}').build(),
        HttpResponse(json.dumps(find_template("user_query", __file__)), 200),
    )
    http_mocker.post(
        RequestBuilder(resource="Accounts/Search").with_body(ACCOUNTS_SEARCH_BODY).build(),
        HttpResponse(json.dumps(find_template(resource="accounts_search_for_report", execution_folder=__file__)), 200),
    )


def _mock_bulk_submit(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        RequestBuilder(resource="Bulk/v13/Campaigns/DownloadByAccountIds", api="bulk")
        .with_body(
            '{"AccountIds": ["180535609"], "DataScope": "EntityData", "DownloadEntities": ["Budgets"], '
            '"DownloadFileType": "Csv", "FormatVersion": "6.0", "CompressionType": "GZip"}'
        )
        .build(),
        HttpResponse(json.dumps(find_template(resource="bulk_download", execution_folder=__file__)), 200),
    )


def _mock_bulk_job(http_mocker: HttpMocker) -> HttpRequest:
    _mock_bulk_submit(http_mocker)
    http_mocker.post(
        RequestBuilder(resource="Bulk/v13/BulkDownloadStatus/Query", api="bulk")
        .with_body('{"RequestId": "TestDownloadRequestId"}')
        .build(),
        HttpResponse(json.dumps(find_template(resource="bulk_status", execution_folder=__file__)), 200),
    )
    return RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()


def _mock_report_job(http_mocker: HttpMocker) -> HttpRequest:
    http_mocker.post(
        RequestBuilder(resource="GenerateReport/Submit", api="reporting")
        .with_body(ACCOUNT_IMPRESSION_PERFORMANCE_REPORT_HOURLY_SUBMIT_BODY)
        .build(),
        HttpResponse(json.dumps(find_template(resource="generate_report", execution_folder=__file__)), 200),
    )
    http_mocker.post(
        RequestBuilder(resource="GenerateReport/Poll", api="reporting")
        .with_body(b'{"ReportRequestId": "thisisthereport_requestid"}')
        .build(),
        HttpResponse(json.dumps(find_template(resource="generate_report_poll", execution_folder=__file__)), 200),
    )
    return RequestBuilder(resource="").build_report_url()


@freeze_time("2024-05-06")
@pytest.mark.parametrize(
    "stream_name, mock_job",
    [
        pytest.param("budget", _mock_bulk_job, id="bulk_stream"),
        pytest.param("account_impression_performance_report_hourly", _mock_report_job, id="report_stream"),
    ],
)
def test_expired_download_url_fails_as_transient_error_naming_the_stream(stream_name, mock_job):
    config = ConfigBuilder().with_reports_start_date("2024-01-01").build()
    with HttpMocker() as http_mocker:
        _mock_accounts(http_mocker, config)
        download_request = mock_job(http_mocker)
        http_mocker.get(download_request, AZURE_SAS_EXPIRED_RESPONSE)

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read_helper(config, catalog, expecting_exception=True)

        assert output.records == []
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.transient_error
        assert error.message == (
            f"The Bing Ads download link for stream '{stream_name}' expired before the file could be downloaded. The sync will retry."
        )
        http_mocker.assert_number_of_calls(download_request, 1)


def _mock_bulk_job_with_stale_then_fresh_url(http_mocker: HttpMocker) -> HttpRequest:
    _mock_bulk_submit(http_mocker)
    status_query_request = (
        RequestBuilder(resource="Bulk/v13/BulkDownloadStatus/Query", api="bulk").with_body('{"RequestId": "TestDownloadRequestId"}').build()
    )
    http_mocker.post(
        status_query_request,
        [
            HttpResponse(json.dumps({"RequestStatus": "Completed", "ResultFileUrl": f"{BULK_BASE_URL}/path/to/stale/url"}), 200),
            HttpResponse(json.dumps({"RequestStatus": "Completed", "ResultFileUrl": f"{BULK_BASE_URL}/path/to/fresh/url"}), 200),
        ],
    )
    http_mocker.get(RequestBuilder(resource="path/to/stale/url", api="bulk").build(), AZURE_SAS_EXPIRED_RESPONSE)
    budget_csv = (Path(__file__).parent.parent / "resource/response/budget.csv").read_text().encode("utf-8-sig")
    http_mocker.get(RequestBuilder(resource="path/to/fresh/url", api="bulk").build(), HttpResponse(budget_csv, 200))
    return status_query_request


def _mock_report_job_with_stale_then_fresh_url(http_mocker: HttpMocker) -> HttpRequest:
    http_mocker.post(
        RequestBuilder(resource="GenerateReport/Submit", api="reporting")
        .with_body(ACCOUNT_IMPRESSION_PERFORMANCE_REPORT_HOURLY_SUBMIT_BODY)
        .build(),
        HttpResponse(json.dumps(find_template(resource="generate_report", execution_folder=__file__)), 200),
    )
    poll_request = (
        RequestBuilder(resource="GenerateReport/Poll", api="reporting")
        .with_body(b'{"ReportRequestId": "thisisthereport_requestid"}')
        .build()
    )
    http_mocker.post(
        poll_request,
        [
            HttpResponse(json.dumps({"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": STALE_REPORT_URL}}), 200),
            HttpResponse(json.dumps({"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": FRESH_REPORT_URL}}), 200),
        ],
    )
    http_mocker.get(HttpRequest(url=STALE_REPORT_URL), AZURE_SAS_EXPIRED_RESPONSE)
    http_mocker.get(
        HttpRequest(url=FRESH_REPORT_URL), HttpResponse(create_zip_from_csv("account_impression_performance_report_hourly"), 200)
    )
    return poll_request


STALE_REPORT_URL = "https://bingadsappsstorageprod.blob.core.windows.net/reports/stale.zip?sig=stale"
FRESH_REPORT_URL = "https://bingadsappsstorageprod.blob.core.windows.net/reports/fresh.zip?sig=fresh"


@freeze_time("2024-05-06")
@pytest.mark.parametrize(
    "stream_name, mock_job, expected_records",
    [
        pytest.param("budget", _mock_bulk_job_with_stale_then_fresh_url, 1, id="bulk_stream"),
        pytest.param("account_impression_performance_report_hourly", _mock_report_job_with_stale_then_fresh_url, 24, id="report_stream"),
    ],
)
def test_download_uses_fresh_url_from_repoll_instead_of_url_from_job_completion(stream_name, mock_job, expected_records):
    config = ConfigBuilder().with_reports_start_date("2024-01-01").build()
    with HttpMocker() as http_mocker:
        _mock_accounts(http_mocker, config)
        poll_request = mock_job(http_mocker)

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read_helper(config, catalog)

        assert output.errors == []
        assert len(output.records) == expected_records
        http_mocker.assert_number_of_calls(poll_request, 2)
