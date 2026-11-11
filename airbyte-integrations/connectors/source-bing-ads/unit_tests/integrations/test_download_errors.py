# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_budget_stream
import test_product_dimension_performance_report
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Expiry [Tue, 10 Nov 2026 00:00:00 GMT]</AuthenticationErrorDetail></Error>"
)
DEFAULT_MESSAGE = "You don't have permission to access this resource."


@pytest.mark.parametrize("stream_kind", ["bulk", "report"])
@pytest.mark.parametrize(
    "headers, body, failure_type, message",
    [
        ({"x-ms-error-code": "AuthenticationFailed"}, EXPIRED_BODY, FailureType.transient_error, "Bing Ads file download URL is expired."),
        ({"X-Ms-Error-Code": "AuthenticationFailed"}, "", FailureType.transient_error, "Bing Ads file download URL is expired."),
        ({}, EXPIRED_BODY, FailureType.transient_error, "Bing Ads file download URL is expired."),
        ({}, "", FailureType.config_error, DEFAULT_MESSAGE),
        (
            {"x-ms-error-code": "AuthorizationFailure"},
            "<Error><Code>AuthorizationFailure</Code></Error>",
            FailureType.config_error,
            DEFAULT_MESSAGE,
        ),
    ],
    ids=["expired", "header_only", "body_only", "plain_403", "other_azure_403"],
)
@freeze_time("2024-05-06")
def test_download_errors(stream_kind, headers, body, failure_type, message, mocker):
    if stream_kind == "bulk":
        scenario = test_budget_stream.TestBudgetStream()
        download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
    else:
        scenario = test_product_dimension_performance_report.TestProductDimensionPerformanceReportDailyStream()
        download_request = RequestBuilder(resource="").build_report_url()

    scenario.setUp()
    try:
        if stream_kind == "bulk":
            mocker.patch.object(scenario, "mock_download")
            scenario.mock_apis(file="budget")
        else:
            scenario.mock_report_apis()
        scenario.http_mocker.get(download_request, HttpResponse(body, 403, headers=headers))
        catalog = CatalogBuilder().with_stream(scenario.stream_name, SyncMode.full_refresh).build()
        output = read_helper(scenario._config, catalog, expecting_exception=True)

        errors = [entry.trace.error for entry in output.errors if entry.trace.error.stream_descriptor]
        assert errors
        assert errors[0].failure_type == failure_type
        if failure_type == FailureType.config_error:
            assert message in errors[0].message
        else:
            assert errors[0].message == message
        if body:
            assert body in errors[0].internal_message
        assert not output.records
    finally:
        scenario.tearDown()
