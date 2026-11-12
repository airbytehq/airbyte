# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import test_app_install_ads_stream
import test_hourly_reports
from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


# What Azure Blob Storage answers when the pre-signed (SAS) download URL returned by Bing Ads is used past its expiry.
_EXPIRED_URL_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\nTime:2026-11-10T20:23:43.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Tue, 10 Nov 2026 19:41:55 GMT] - "
    "Expiry [Tue, 10 Nov 2026 20:06:55 GMT] - Current [Tue, 10 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
_AZURE_ERROR_HEADERS = {"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"}
_EXPIRED_URL_RESPONSE = HttpResponse(_EXPIRED_URL_BODY, 403, _AZURE_ERROR_HEADERS)

# A 403 from the same storage host that is not an expired link (the signature itself is rejected).
_OTHER_FORBIDDEN_RESPONSE = HttpResponse(
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationPermissionMismatch</Code>'
    "<Message>This request is not authorized to perform this operation using this permission.</Message></Error>",
    403,
    {"Content-Type": "application/xml", "x-ms-error-code": "AuthorizationPermissionMismatch"},
)

_EXPIRED_URL_MESSAGE = "Bing Ads file download URL is expired."
# The CDK's message for a 403 no connector handler claims; its wording differs between CDK versions.
_DEFAULT_FORBIDDEN_MESSAGE = DEFAULT_ERROR_MAPPING[403].error_message


class _DownloadUrlExpiryTest(BaseTest):
    """
    Serves a 403 on the file download of an async stream and reads the stream through the real entrypoint.

    Subclasses pick the stream and mock every request up to the download.
    """

    stream_name: str

    def setUp(self) -> None:
        if type(self) is _DownloadUrlExpiryTest:
            self.skipTest("Base class")
        super().setUp()

    def _mock_apis_before_download(self) -> None:
        raise NotImplementedError

    def _download_request(self):
        raise NotImplementedError

    def _read_with_download_response(self, response: HttpResponse):
        self._mock_apis_before_download()
        self._mocked_download_request = self._download_request()
        self.http_mocker.get(self._mocked_download_request, response)
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, expecting_exception=True)

    def _stream_errors(self, output):
        return [error for error in output.errors if error.trace.error.stream_descriptor]

    @freeze_time("2024-05-06")
    def test_expired_download_url_fails_as_transient_error_without_retry(self):
        output = self._read_with_download_response(_EXPIRED_URL_RESPONSE)

        assert output.records == []
        errors = self._stream_errors(output)
        assert [(e.trace.error.stream_descriptor.name, e.trace.error.failure_type, e.trace.error.message) for e in errors] == [
            (self.stream_name, FailureType.transient_error, _EXPIRED_URL_MESSAGE)
        ]
        # The raw storage response stays available for debugging, but not in the user-facing message.
        assert "Signature not valid in the specified time frame" in errors[0].trace.error.internal_message
        # Resending the same expired URL cannot succeed, so the download is not retried.
        self.http_mocker.assert_number_of_calls(self._mocked_download_request, 1)

    @freeze_time("2024-05-06")
    def test_other_forbidden_download_keeps_default_classification(self):
        output = self._read_with_download_response(_OTHER_FORBIDDEN_RESPONSE)

        assert output.records == []
        errors = self._stream_errors(output)
        assert [(e.trace.error.stream_descriptor.name, e.trace.error.failure_type, e.trace.error.message) for e in errors] == [
            (self.stream_name, FailureType.config_error, _DEFAULT_FORBIDDEN_MESSAGE)
        ]
        self.http_mocker.assert_number_of_calls(self._mocked_download_request, 1)


class TestBulkDownloadUrlExpiry(_DownloadUrlExpiryTest):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def _mock_apis_before_download(self) -> None:
        bulk = test_app_install_ads_stream.TestAppInstallAdsStream
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        bulk.mock_bulk_download_request(self)
        bulk.mock_bulk_download_status_query(self)

    def _download_request(self):
        return RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()


class TestReportDownloadUrlExpiry(_DownloadUrlExpiryTest):
    stream_name = "ad_performance_report_hourly"

    @property
    def _config(self):
        return ConfigBuilder().with_reports_start_date("2024-01-01").build()

    def _mock_apis_before_download(self) -> None:
        test_hourly_reports.TestAdPerformanceReportHourlyStream.mock_report_apis(self)

    def _download_request(self):
        return RequestBuilder(resource="").build_report_url()
