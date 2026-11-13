# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

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


# Body and header Azure Blob Storage returns for a pre-signed (SAS) download URL used after its expiry time.
EXPIRED_SAS_URL_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:11111111-2222-3333-4444-555555555555\nTime:2026-11-10T20:23:43.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Tue, 10 Nov 2026 19:41:55 GMT] - "
    "Expiry [Tue, 10 Nov 2026 20:06:55 GMT] - Current [Tue, 10 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
EXPIRED_SAS_URL_HEADERS = {"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"}

EXPIRED_URL_MESSAGE = "Bing Ads file download URL is expired or no longer valid."
BULK_STREAM = "app_install_ads"
REPORT_STREAM = "age_gender_audience_report_hourly"


class TestExpiredDownloadUrl(BaseTest):
    @property
    def _config(self):
        return ConfigBuilder().with_reports_start_date("2024-01-01").build()

    def _mock_bulk_job(self) -> HttpRequest:
        """Mock everything a bulk stream needs up to the file download and return the download request."""
        self.download_entity = "AppInstallAds"
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        test_bulk_stream.TestBulkStream.mock_bulk_download_request(self)
        test_bulk_stream.TestBulkStream.mock_bulk_download_status_query(self)
        return RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()

    def _mock_report_job(self) -> HttpRequest:
        """Mock everything a report stream needs up to the file download and return the download request."""
        test_hourly_reports.TestAgeGenderAudienceReportHourlyStream.mock_report_apis(self)
        return RequestBuilder().build_report_url()

    def _read(self, stream_name: str) -> EntrypointOutput:
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, expecting_exception=True)

    def _assert_single_failure(
        self, output: EntrypointOutput, stream_name: str, download_request: HttpRequest, failure_type: FailureType, message: str
    ):
        assert output.records == []
        # The first error is the stream's failure; the sync-level summary that follows repeats it.
        stream_error = output.errors[0].trace.error
        assert (stream_error.stream_descriptor.name, stream_error.failure_type, stream_error.message) == (
            stream_name,
            failure_type,
            message,
        )
        # The download is attempted once: resending the same expired URL cannot succeed.
        self.http_mocker.assert_number_of_calls(download_request, 1)

    def test_bulk_stream_expired_download_url_is_a_transient_error(self):
        download_request = self._mock_bulk_job()
        self.http_mocker.get(download_request, HttpResponse(EXPIRED_SAS_URL_BODY, 403, EXPIRED_SAS_URL_HEADERS))

        output = self._read(BULK_STREAM)

        self._assert_single_failure(output, BULK_STREAM, download_request, FailureType.transient_error, EXPIRED_URL_MESSAGE)

    @freeze_time("2024-05-06")
    def test_report_stream_expired_download_url_is_a_transient_error(self):
        download_request = self._mock_report_job()
        self.http_mocker.get(download_request, HttpResponse(EXPIRED_SAS_URL_BODY, 403, EXPIRED_SAS_URL_HEADERS))

        output = self._read(REPORT_STREAM)

        self._assert_single_failure(output, REPORT_STREAM, download_request, FailureType.transient_error, EXPIRED_URL_MESSAGE)
