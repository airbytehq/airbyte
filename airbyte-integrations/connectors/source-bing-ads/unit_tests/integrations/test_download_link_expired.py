# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_app_install_ads_stream as bulk_tests
import test_product_search_query_performance_report as report_tests
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import REPORT_URL, RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


# What Azure Blob Storage answers when the pre-signed download link issued by Bing Ads is past its expiry time.
EXPIRED_LINK_RESPONSE = HttpResponse(
    body=(
        '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
        "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
        "including the signature.</Message>"
        "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Mon, 06 May 2024 00:00:00 GMT] - "
        "Expiry [Mon, 06 May 2024 00:10:00 GMT] - Current [Mon, 06 May 2024 00:11:00 GMT]</AuthenticationErrorDetail></Error>"
    ),
    status_code=403,
    headers={"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"},
)


def _mock_bulk_stream(test_case) -> HttpRequest:
    test_case.mock_user_query_api(response_template="user_query")
    test_case.mock_accounts_search_api(
        response_template="accounts_search_for_report",
        body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
    )
    test_case.mock_bulk_download_request()
    test_case.mock_bulk_download_status_query()
    return RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()


def _mock_report_stream(test_case) -> HttpRequest:
    test_case.mock_report_apis()
    return HttpRequest(url=REPORT_URL)


@freeze_time("2024-05-06")
@pytest.mark.parametrize(
    "test_case_class, mock_stream",
    [
        pytest.param(bulk_tests.TestAppInstallAdsStream, _mock_bulk_stream, id="bulk_stream"),
        pytest.param(report_tests.TestProductSearchQueryPerformanceReportDailyStream, _mock_report_stream, id="report_stream"),
    ],
)
def test_expired_download_link_fails_stream_as_transient_error(test_case_class, mock_stream):
    # The existing stream test cases are only used for their HTTP mocks of the requests that precede the download.
    test_case = test_case_class("test_return_records_from_given_csv_file")
    test_case.setUp()
    try:
        download_request = mock_stream(test_case)
        test_case.http_mocker.get(download_request, EXPIRED_LINK_RESPONSE)

        catalog = CatalogBuilder().with_stream(test_case.stream_name, SyncMode.full_refresh).build()
        output = read_helper(test_case._config, catalog, expecting_exception=True)

        assert output.records == []
        # The first error trace is the one attributed to the stream; the CDK follows it with a generic end-of-sync summary.
        error = output.errors[0].trace.error
        assert error.stream_descriptor.name == test_case.stream_name
        assert error.failure_type == FailureType.transient_error
        assert error.message == (
            "Bing Ads file download link is expired or no longer valid. The download request was rejected by Microsoft file storage."
        )
        # The link stays expired, so the same link is not requested again.
        test_case.http_mocker.assert_number_of_calls(download_request, 1)
    finally:
        test_case.tearDown()
