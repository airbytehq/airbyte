# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
from typing import Any, Optional

import test_bulk_stream
import test_hourly_reports
from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


# What Azure Blob Storage returns for a pre-signed (SAS) download URL whose validity window is over.
EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\nTime:2026-11-10T20:23:43.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Tue, 10 Nov 2026 19:41:55 GMT] - "
    "Expiry [Tue, 10 Nov 2026 20:06:55 GMT] - Current [Tue, 10 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
# A 403 from the same storage host that is not about the validity window of the URL.
OTHER_403_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationPermissionMismatch</Code>'
    "<Message>This request is not authorized to perform this operation using this permission.</Message></Error>"
)

EXPIRED_URL_MESSAGE = "Bing Ads file download URL is expired."
# The CDK's default message for a 403. Newer CDK versions prefix it with "HTTP Status Code: 403. Error: ".
DEFAULT_403_MESSAGE = "Forbidden. You don't have permission to access this resource."


class DownloadUrlExpiryMixin:
    """
    Reads a stream whose file download answers 403. The classes below bind it to one bulk stream and one report
    stream, because the two families download through different requesters.
    """

    stream_name: Optional[str] = None

    def _mock_apis_up_to_download(self) -> None:
        raise NotImplementedError

    def _download_request(self) -> HttpRequest:
        raise NotImplementedError

    def _read_with_failing_download(self, body: str, error_code: str) -> EntrypointOutput:
        self._mock_apis_up_to_download()
        self._download = self._download_request()
        self.http_mocker.get(self._download, HttpResponse(body, 403, headers={"x-ms-error-code": error_code}))
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, expecting_exception=True)

    def _assert_single_failed_download(self, output: EntrypointOutput, failure_type: FailureType, message: str) -> None:
        assert len(output.records) == 0
        # The read also ends with a source-wide error that has no stream; the stream's own error carries the classification.
        stream_errors = [message.trace.error for message in output.errors if message.trace.error.stream_descriptor]
        assert len(stream_errors) == 1
        error = stream_errors[0]
        assert error.failure_type == failure_type
        assert error.message.endswith(message) if message == DEFAULT_403_MESSAGE else error.message == message
        assert error.stream_descriptor.name == self.stream_name
        # The same URL stays expired, so the download is not sent again.
        self.http_mocker.assert_number_of_calls(self._download, 1)

    @freeze_time("2024-05-06")
    def test_expired_download_url_fails_as_transient_error(self):
        output = self._read_with_failing_download(EXPIRED_SAS_BODY, "AuthenticationFailed")

        self._assert_single_failed_download(output, FailureType.transient_error, EXPIRED_URL_MESSAGE)
        # The storage response stays available for debugging.
        assert any("Signature not valid in the specified time frame" in message.trace.error.internal_message for message in output.errors)

    @freeze_time("2024-05-06")
    def test_other_download_403_keeps_permission_error(self):
        output = self._read_with_failing_download(OTHER_403_BODY, "AuthorizationPermissionMismatch")

        self._assert_single_failed_download(output, FailureType.config_error, DEFAULT_403_MESSAGE)


class TestBulkDownloadUrlExpiry(DownloadUrlExpiryMixin, test_bulk_stream.TestBulkStream):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def _mock_apis_up_to_download(self) -> None:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()

    def _download_request(self) -> HttpRequest:
        return RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()


class TestReportDownloadUrlExpiry(DownloadUrlExpiryMixin, BaseTest):
    stream_name = "ad_performance_report_hourly"

    @property
    def _config(self) -> dict[str, Any]:
        return ConfigBuilder().with_reports_start_date("2024-01-01").build()

    def _mock_apis_up_to_download(self) -> None:
        test_hourly_reports.TestAdPerformanceReportHourlyStream.mock_report_apis(self)

    def _download_request(self) -> HttpRequest:
        return RequestBuilder(resource="").build_report_url()
