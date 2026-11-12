# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import test_product_dimension_performance_report as report_tests
from base_test import create_zip_from_csv
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from test_bulk_stream import TestBulkStream as BulkHarness

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


@pytest.fixture
def harness():
    helper = BulkHarness()
    helper.download_entity = "Budgets"
    helper.setUp()
    yield helper
    helper.tearDown()


def read_stream(stream, expecting_exception=False):
    return read_helper(
        ConfigBuilder().with_reports_start_date("2024-01-01").build(),
        CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build(),
        expecting_exception=expecting_exception,
    )


def mock_job(harness, stream, responses):
    if stream == "budget":
        harness.mock_user_query_api("user_query")
        harness.mock_accounts_search_api(
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
            response_template="accounts_search_for_report",
        )
        harness.mock_bulk_download_request()
        request = RequestBuilder(resource="Bulk/v13/BulkDownloadStatus/Query", api="bulk").with_body(
            '{"RequestId": "TestDownloadRequestId"}'
        ).build()
    else:
        report = report_tests.TestProductDimensionPerformanceReportDailyStream()
        report._http_mocker = harness.http_mocker
        generate_report = report.mock_generate_report_api

        def mock_generate_report(endpoint, body, response_template):
            if endpoint == "Submit":
                generate_report(endpoint, body, response_template)

        with patch.object(report, "mock_generate_report_api", side_effect=mock_generate_report):
            report.mock_report_apis()
        request = RequestBuilder(resource="GenerateReport/Poll", api="reporting").with_body(
            '{"ReportRequestId": "thisisthereport_requestid"}'
        ).build()
    harness.http_mocker.post(request, responses)


def poll_response(stream, url=None):
    status = find_template("bulk_status" if stream == "budget" else "generate_report_poll", __file__)
    if stream == "budget":
        if url:
            status["ResultFileUrl"] = url
        return status, status["ResultFileUrl"]
    if url:
        status["ReportRequestStatus"]["ReportDownloadUrl"] = url
    return status, status["ReportRequestStatus"]["ReportDownloadUrl"]


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream,count", [("budget", 1), ("product_dimension_performance_report_daily", 8)])
def test_download_uses_fresh_url(harness, stream, count):
    original, stale_url = poll_response(stream)
    fresh, fresh_url = poll_response(stream, "https://bulk.api.bingads.microsoft.com/fresh.csv")
    mock_job(harness, stream, [HttpResponse(json.dumps(original)), HttpResponse(json.dumps(fresh))])
    download = HttpRequest(url=fresh_url)
    content = (
        (Path(__file__).parent.parent / "resource/response/budget.csv").read_bytes()
        if stream == "budget" else create_zip_from_csv(stream)
    )
    harness.http_mocker.get(download, HttpResponse(content))

    output = read_stream(stream, expecting_exception=True)

    assert len(output.records) == count
    assert {record.record.data["Id" if stream == "budget" else "AdId"] for record in output.records} == (
        {-20} if stream == "budget" else {12345}
    )
    harness.http_mocker.assert_number_of_calls(download, 1)
    assert not any(request.url == stale_url for request in harness.http_mocker._mocker.request_history)


@pytest.mark.parametrize("stream", ["budget", "product_dimension_performance_report_daily"])
@freeze_time("2024-05-06")
def test_download_xml_error(harness, stream):
    status, url = poll_response(stream)
    mock_job(harness, stream, [HttpResponse(json.dumps(status)), HttpResponse(json.dumps(status))])
    download = HttpRequest(url=url)
    harness.http_mocker.get(
        download,
        HttpResponse(
            '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
            "<Message>Signature not valid in the specified time frame</Message></Error>",
            403,
            headers={"Content-Type": "application/xml"},
        ),
    )

    output = read_stream(stream, expecting_exception=True)

    errors = [trace.trace.error for trace in output.errors]
    assert errors
    assert errors[0].failure_type == FailureType.transient_error
    assert errors[0].message == (
        "The Bing Ads download link expired before the file could be downloaded. The sync will retry."
    )
