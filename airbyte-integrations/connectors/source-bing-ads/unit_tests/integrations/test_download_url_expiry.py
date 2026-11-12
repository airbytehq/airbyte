# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""
Bing Ads returns pre-signed Azure Blob Storage URLs for bulk and report files. When such a URL expires before the
file is downloaded, Azure answers with ``403 AuthenticationFailed`` and the body text
``Signature not valid in the specified time frame``. That is not a permission problem, so the connector must not
surface the generic "You don't have permission" ``config_error``.
"""

import test_bulk_stream
import test_product_dimension_performance_report
from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_SIGNATURE_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code><Message>Server failed to authenticate '
    "the request. Make sure the value of Authorization header is formed correctly including the signature.\n"
    "RequestId:00000000-0000-0000-0000-000000000000\nTime:2025-01-01T20:23:43.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Wed, 01 Jan 2025 19:41:55 GMT] - "
    "Expiry [Wed, 01 Jan 2025 20:06:55 GMT] - Current [Wed, 01 Jan 2025 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
OTHER_FORBIDDEN_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationPermissionMismatch</Code>'
    "<Message>This request is not authorized to perform this operation using this permission.</Message></Error>"
)
EXPIRED_URL_MESSAGE = "Bing Ads file download URL is expired."
PERMISSION_MESSAGE = "Forbidden. You don't have permission to access this resource."


def _forbidden(body: str, error_code: str) -> HttpResponse:
    return HttpResponse(body, 403, headers={"Content-Type": "application/xml", "x-ms-error-code": error_code})


def _single_trace_error(output: EntrypointOutput):
    errors = [message.trace.error for message in output.errors]
    assert errors, "expected the sync to emit an error trace message"
    return errors[0]


# Imported as modules so pytest does not collect the imported test suites a second time.
class TestBulkStreamDownloadUrlExpiry(test_bulk_stream.TestBulkStream):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def _mock_bulk_apis_with_download_response(self, response: HttpResponse) -> None:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        self.http_mocker.get(RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build(), response)

    def _read(self) -> EntrypointOutput:
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, expecting_exception=True)

    def test_expired_download_url_fails_as_transient_error_with_specific_message(self):
        self._mock_bulk_apis_with_download_response(_forbidden(EXPIRED_SIGNATURE_BODY, "AuthenticationFailed"))

        output = self._read()

        assert not output.records
        error = _single_trace_error(output)
        assert error.failure_type == FailureType.transient_error
        assert error.message == EXPIRED_URL_MESSAGE
        assert error.stream_descriptor.name == self.stream_name

    def test_other_forbidden_download_keeps_permission_config_error(self):
        self._mock_bulk_apis_with_download_response(_forbidden(OTHER_FORBIDDEN_BODY, "AuthorizationPermissionMismatch"))

        output = self._read()

        assert not output.records
        error = _single_trace_error(output)
        assert error.failure_type == FailureType.config_error
        assert PERMISSION_MESSAGE in error.message


class TestReportStreamDownloadUrlExpiry(BaseTest):
    stream_name = "product_dimension_performance_report_daily"

    @property
    def _config(self):
        return ConfigBuilder().with_reports_start_date("2024-01-01").build()

    def _mock_report_apis_with_download_response(self, response: HttpResponse) -> None:
        # Reuse the user/accounts/Submit/Poll mocks of the report stream suite without inheriting its test methods.
        report_suite = test_product_dimension_performance_report.TestProductDimensionPerformanceReportDailyStream("mock_report_apis")
        report_suite._http_mocker = self.http_mocker
        report_suite.mock_report_apis()
        self.http_mocker.get(RequestBuilder(resource="").build_report_url(), response)

    def _read(self) -> EntrypointOutput:
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, expecting_exception=True)

    @freeze_time("2024-05-06")
    def test_expired_download_url_fails_as_transient_error_with_specific_message(self):
        self._mock_report_apis_with_download_response(_forbidden(EXPIRED_SIGNATURE_BODY, "AuthenticationFailed"))

        output = self._read()

        assert not output.records
        error = _single_trace_error(output)
        assert error.failure_type == FailureType.transient_error
        assert error.message == EXPIRED_URL_MESSAGE
        assert error.stream_descriptor.name == self.stream_name
