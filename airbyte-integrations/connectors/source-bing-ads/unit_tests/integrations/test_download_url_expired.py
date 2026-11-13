# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import test_bulk_stream
import test_custom_report
from base_test import BaseTest
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.</Message><AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [Thu, 12 Nov 2026 19:41:55 GMT] - Expiry [Thu, 12 Nov 2026 20:06:55 GMT] - Current [Thu, 12 Nov 2026 20:23:43 GMT]"
    "</AuthenticationErrorDetail></Error>"
)
EXPIRED_SAS_HEADERS = {"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"}
EXPECTED_MESSAGE = "Bing Ads file download URL is expired or invalid."


def _stream_errors(output, stream_name: str):
    return [
        message.trace.error
        for message in output.errors
        if message.trace.error.stream_descriptor and message.trace.error.stream_descriptor.name == stream_name
    ]


def _assert_single_transient_expired_url_error(output, stream_name: str) -> None:
    errors = _stream_errors(output, stream_name)
    assert len(errors) == 1
    assert errors[0].failure_type == FailureType.transient_error
    assert errors[0].message == EXPECTED_MESSAGE
    assert "Signature not valid in the specified time frame" in errors[0].internal_message


class TestBulkStreamDownloadUrlExpired(test_bulk_stream.TestBulkStream):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def _mock_bulk_download_file(self, response: HttpResponse) -> None:
        self.http_mocker.get(RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build(), response)

    def test_expired_download_url_fails_as_transient_error(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        self._mock_bulk_download_file(HttpResponse(EXPIRED_SAS_BODY, 403, EXPIRED_SAS_HEADERS))

        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, "app_install_ads", expecting_exception=True)

        assert output.records == []
        _assert_single_transient_expired_url_error(output, self.stream_name)

    def test_other_403_on_download_keeps_default_classification(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        self._mock_bulk_download_file(
            HttpResponse(
                '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationPermissionMismatch</Code></Error>',
                403,
                {"Content-Type": "application/xml", "x-ms-error-code": "AuthorizationPermissionMismatch"},
            )
        )

        output = self.read_stream(self.stream_name, SyncMode.full_refresh, self._config, "app_install_ads", expecting_exception=True)

        errors = _stream_errors(output, self.stream_name)
        assert len(errors) == 1
        assert errors[0].failure_type == FailureType.config_error
        assert "You don't have permission to access this resource." in errors[0].message


class TestReportStreamDownloadUrlExpired(BaseTest):
    stream_name = test_custom_report.TestCustomReportDaily.stream_name
    start_date = test_custom_report.TestCustomReportDaily.start_date
    custom_report_aggregation = test_custom_report.TestCustomReportDaily.custom_report_aggregation
    _config = test_custom_report.TestCustomReportDaily._config
    mock_base_requests = test_custom_report.TestCustomReportDaily.mock_base_requests
    _mock_report_apis = test_custom_report.TestCustomReportDaily._mock_report_apis

    @freeze_time("2024-05-06")
    def test_expired_report_download_url_fails_as_transient_error(self):
        self.mock_base_requests()
        self._mock_report_apis()
        self.http_mocker.get(
            RequestBuilder(resource="").build_report_url(),
            HttpResponse(EXPIRED_SAS_BODY, 403, EXPIRED_SAS_HEADERS),
        )
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()

        output = read_helper(self._config, catalog, expecting_exception=True)

        assert output.records == []
        _assert_single_transient_expired_url_error(output, self.stream_name)
