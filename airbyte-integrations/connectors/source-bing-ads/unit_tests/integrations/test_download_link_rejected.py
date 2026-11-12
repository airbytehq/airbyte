# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

# The suites are referenced through their modules so pytest does not collect them a second time here.
import pytest
import test_app_install_ads_stream as bulk_suite
import test_custom_report as custom_report_suite
import test_hourly_reports as report_suite
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


# Body and header Azure Blob Storage returns for a pre-signed download link outside its validity window.
AZURE_REJECTED_LINK_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Mon, 06 May 2024 00:00:00 GMT] - "
    "Expiry [Mon, 06 May 2024 00:10:00 GMT] - Current [Mon, 06 May 2024 00:11:00 GMT]</AuthenticationErrorDetail></Error>"
)
AZURE_REJECTED_LINK_HEADERS = {"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"}


def _mock_bulk_stream(suite):
    suite.mock_user_query_api(response_template="user_query")
    suite.mock_accounts_search_api(
        response_template="accounts_search_for_report",
        body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
    )
    suite.mock_bulk_download_request()
    suite.mock_bulk_download_status_query()
    return RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()


def _mock_report_stream(suite):
    suite.mock_report_apis()
    return RequestBuilder(resource="").build_report_url()


@pytest.mark.parametrize(
    "suite_class, mock_stream",
    [
        pytest.param(bulk_suite.TestAppInstallAdsStream, _mock_bulk_stream, id="bulk_stream"),
        pytest.param(report_suite.TestAdPerformanceReportHourlyStream, _mock_report_stream, id="report_stream"),
        pytest.param(custom_report_suite.TestCustomReportDaily, _mock_report_stream, id="custom_report_stream"),
    ],
)
@freeze_time("2024-05-06")
def test_rejected_download_link_fails_as_transient_error_naming_the_stream(suite_class, mock_stream):
    suite = suite_class()
    suite.setUp()
    try:
        download_request = mock_stream(suite)
        suite.http_mocker.get(download_request, HttpResponse(AZURE_REJECTED_LINK_BODY, 403, AZURE_REJECTED_LINK_HEADERS))
        catalog = CatalogBuilder().with_stream(suite.stream_name, SyncMode.full_refresh).build()

        output = read_helper(suite._config, catalog, expecting_exception=True)

        assert output.records == []
        stream_errors = [error.trace.error for error in output.errors if error.trace.error.stream_descriptor]
        assert len(stream_errors) == 1
        assert stream_errors[0].failure_type == FailureType.transient_error
        assert stream_errors[0].message == (
            f"Bing Ads file download link for stream '{suite.stream_name}' is expired or not valid. "
            "Microsoft storage rejected the download request."
        )
        # The same link cannot become valid again, so the download is not repeated.
        suite.http_mocker.assert_number_of_calls(download_request, 1)
    finally:
        suite.tearDown()
