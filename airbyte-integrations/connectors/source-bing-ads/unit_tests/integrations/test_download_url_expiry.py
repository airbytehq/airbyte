# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import pytest
import test_app_install_ads_stream as bulk_tests
import test_hourly_reports as report_tests
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_URL_MESSAGE = "Bing Ads file download URL is expired."
DEFAULT_403_MESSAGE = "Forbidden. You don't have permission to access this resource."

# Body returned by Azure Blob Storage when the pre-signed (SAS) download URL is requested after its expiry time.
EXPIRED_SIGNATURE_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\nTime:2026-11-10T20:23:43.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Tue, 10 Nov 2026 19:41:55 GMT] - "
    "Expiry [Tue, 10 Nov 2026 20:06:55 GMT] - Current [Tue, 10 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
# A 403 from Azure Blob Storage that is not about the validity window of the signature.
OTHER_FORBIDDEN_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationPermissionMismatch</Code>'
    "<Message>This request is not authorized to perform this operation using this permission.</Message></Error>"
)


def _mock_bulk_stream(response: HttpResponse):
    test_case = bulk_tests.TestAppInstallAdsStream("mock_apis")
    test_case.setUp()
    test_case.mock_user_query_api(response_template="user_query")
    test_case.mock_accounts_search_api(
        response_template="accounts_search_for_report",
        body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
    )
    test_case.mock_bulk_download_request()
    test_case.mock_bulk_download_status_query()
    download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
    test_case.http_mocker.get(download_request, response)
    return test_case, download_request


def _mock_report_stream(response: HttpResponse):
    test_case = report_tests.TestAdPerformanceReportHourlyStream("mock_report_apis")
    test_case.setUp()
    test_case.mock_report_apis()
    download_request = RequestBuilder(resource="").build_report_url()
    test_case.http_mocker.get(download_request, response)
    return test_case, download_request


@pytest.mark.parametrize(
    "mock_stream, response_body, error_code, expected_message, expected_failure_type",
    [
        pytest.param(
            _mock_bulk_stream,
            EXPIRED_SIGNATURE_BODY,
            "AuthenticationFailed",
            EXPIRED_URL_MESSAGE,
            FailureType.transient_error,
            id="bulk-expired",
        ),
        pytest.param(
            _mock_report_stream,
            EXPIRED_SIGNATURE_BODY,
            "AuthenticationFailed",
            EXPIRED_URL_MESSAGE,
            FailureType.transient_error,
            id="report-expired",
        ),
        pytest.param(
            _mock_bulk_stream,
            OTHER_FORBIDDEN_BODY,
            "AuthorizationPermissionMismatch",
            DEFAULT_403_MESSAGE,
            FailureType.config_error,
            id="bulk-other-403",
        ),
        pytest.param(
            _mock_report_stream,
            OTHER_FORBIDDEN_BODY,
            "AuthorizationPermissionMismatch",
            DEFAULT_403_MESSAGE,
            FailureType.config_error,
            id="report-other-403",
        ),
    ],
)
@freeze_time("2024-05-06")
def test_403_on_file_download_is_classified_by_azure_error(mock_stream, response_body, error_code, expected_message, expected_failure_type):
    test_case, download_request = mock_stream(HttpResponse(response_body, 403, headers={"x-ms-error-code": error_code}))
    try:
        catalog = CatalogBuilder().with_stream(test_case.stream_name, SyncMode.full_refresh).build()
        output = read_helper(test_case._config, catalog, None, expecting_exception=True)

        assert output.records == []
        # The first error is the stream failure. The CDK appends its own end-of-sync summary error after it.
        stream_error = output.errors[0].trace.error
        assert stream_error.stream_descriptor.name == test_case.stream_name
        # The CDK default 403 message gained an "HTTP Status Code: 403. Error: " prefix in later CDK versions.
        assert stream_error.message.removeprefix("HTTP Status Code: 403. Error: ") == expected_message
        assert stream_error.failure_type == expected_failure_type
        # The same URL stays expired, so the download is not retried.
        test_case.http_mocker.assert_number_of_calls(download_request, 1)
    finally:
        test_case.tearDown()
