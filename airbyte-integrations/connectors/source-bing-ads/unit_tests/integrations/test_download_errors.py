# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_product_dimension_performance_report as report_tests
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from test_bulk_stream import TestBulkStream

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


@pytest.mark.parametrize("stream_name", ["app_install_ads", "product_dimension_performance_report_daily"])
@pytest.mark.parametrize("expired", [True, False])
@freeze_time("2024-05-06")
def test_download_forbidden(stream_name, expired):
    harness = TestBulkStream() if stream_name == "app_install_ads" else report_tests.TestProductDimensionPerformanceReportDailyStream()
    harness.setUp()
    try:
        if stream_name == "app_install_ads":
            harness.mock_user_query_api(response_template="user_query")
            harness.mock_accounts_search_api(
                response_template="accounts_search_for_report",
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
            )
            harness.download_entity = "AppInstallAds"
            harness.mock_bulk_download_request()
            harness.mock_bulk_download_status_query()
            download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        else:
            harness.mock_report_apis()
            download_request = RequestBuilder().build_report_url()

        body = (
            '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
            "<Message>Server failed to authenticate the request.</Message><AuthenticationErrorDetail>"
            "Signature not valid in the specified time frame: Start [2024-05-06T00:00:00Z] - "
            "Expiry [2024-05-06T00:10:00Z] - Current [2024-05-06T01:00:00Z]"
            "</AuthenticationErrorDetail></Error>"
            if expired
            else ""
        )
        headers = {"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"} if expired else {}
        harness.http_mocker.get(download_request, HttpResponse(body, 403, headers))
        config = ConfigBuilder().with_reports_start_date("2024-01-01").build()
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read_helper(config, catalog, expecting_exception=True)

        assert not output.records
        errors = [message.trace.error for message in output.errors]
        assert errors
        expected_type = FailureType.transient_error if expired else FailureType.config_error
        assert errors[0].failure_type == expected_type
        if expired:
            assert errors[0].message == "Bing Ads file download URL is expired."
        else:
            assert "You don't have permission to access this resource." in errors[0].message
    finally:
        harness.tearDown()
