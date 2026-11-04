# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_SIGNATURE_RESPONSE = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [Mon, 03 Nov 2026 10:00:00 GMT] - Expiry [Mon, 03 Nov 2026 10:10:00 GMT] "
    "- Current [Mon, 03 Nov 2026 10:25:00 GMT]</AuthenticationErrorDetail></Error>"
)
PERMISSION_MISMATCH_RESPONSE = (
    "<Error><Code>AuthorizationPermissionMismatch</Code>"
    "<Message>This request is not authorized to perform this operation using this permission.</Message></Error>"
)
EXPECTED_EXPIRED_LINK_MESSAGE = (
    "The Bing Ads file download link expired or was not yet valid when the connector tried to download "
    "the file. This is a temporary issue; the sync will be retried."
)


class TestDownloadErrors:
    def _read_report(self, response_body):
        from test_product_dimension_performance_report import (
            TestProductDimensionPerformanceReportDailyStream,
        )

        stream_test = TestProductDimensionPerformanceReportDailyStream("test_return_records_from_given_csv_file")
        stream_test.setUp()
        try:
            stream_test.mock_report_apis()
            stream_test.http_mocker.get(
                RequestBuilder(resource="").build_report_url(),
                HttpResponse(response_body, 403),
            )
            catalog = CatalogBuilder().with_stream("product_dimension_performance_report_daily", SyncMode.full_refresh).build()
            return read_helper(stream_test._config, catalog, expecting_exception=True)
        finally:
            stream_test.tearDown()

    def _read_bulk(self, response_body):
        from test_budget_stream import TestBudgetStream

        stream_test = TestBudgetStream("test_return_records_from_given_csv_file")
        stream_test.setUp()
        try:
            stream_test.mock_user_query_api(response_template="user_query")
            stream_test.mock_accounts_search_api(
                response_template="accounts_search_for_report",
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
            )
            stream_test.mock_bulk_download_request()
            stream_test.mock_bulk_download_status_query()
            stream_test.http_mocker.get(
                RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build(),
                HttpResponse(response_body, 403),
            )
            catalog = CatalogBuilder().with_stream("budget", SyncMode.full_refresh).build()
            return read_helper(stream_test._config, catalog, expecting_exception=True)
        finally:
            stream_test.tearDown()

    @freeze_time("2024-05-06")
    def test_expired_signature_report_download_is_transient(self):
        output = self._read_report(EXPIRED_SIGNATURE_RESPONSE)
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.transient_error, f"{error.failure_type=}, {error.message=}"
        assert error.message == EXPECTED_EXPIRED_LINK_MESSAGE

    def test_expired_signature_bulk_download_is_transient(self):
        output = self._read_bulk(EXPIRED_SIGNATURE_RESPONSE)
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.transient_error, f"{error.failure_type=}, {error.message=}"
        assert error.message == EXPECTED_EXPIRED_LINK_MESSAGE

    @freeze_time("2024-05-06")
    def test_permission_mismatch_report_download_remains_config_error(self):
        output = self._read_report(PERMISSION_MISMATCH_RESPONSE)
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
