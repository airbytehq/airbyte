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


# What Azure Blob Storage answers when the pre-signed (SAS) download URL handed out by Bing Ads is used outside its validity window.
AZURE_EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly including the signature.\n"
    "RequestId:00000000-0000-0000-0000-000000000000\nTime:2024-05-06T00:20:00.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Mon, 06 May 2024 00:00:00 GMT] - "
    "Expiry [Mon, 06 May 2024 00:10:00 GMT] - Current [Mon, 06 May 2024 00:20:00 GMT]</AuthenticationErrorDetail></Error>"
)
AZURE_EXPIRED_SAS_RESPONSE = HttpResponse(AZURE_EXPIRED_SAS_BODY, 403, headers={"x-ms-error-code": "AuthenticationFailed"})


class ExpiredDownloadLinkMixin:
    stream_name: str

    def read_with_expired_download_link(self, download_request: HttpRequest, config: dict) -> EntrypointOutput:
        self.http_mocker.get(download_request, AZURE_EXPIRED_SAS_RESPONSE)
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(config, catalog, expecting_exception=True)

    def assert_fails_as_transient_expired_link(self, output: EntrypointOutput, download_request: HttpRequest) -> None:
        assert len(output.records) == 0
        # The first trace is the stream failure. The CDK follows it with a sync-level summary trace whose failure type is always
        # config_error, whatever the stream failed with, so only the stream failure is asserted.
        stream_error = output.errors[0].trace.error
        assert (stream_error.failure_type, stream_error.message, stream_error.stream_descriptor.name) == (
            FailureType.transient_error,
            "Bing Ads file download link is rejected by Microsoft file storage. The pre-signed link is expired or no longer valid.",
            self.stream_name,
        )
        # The link is not downloaded again: retrying the same pre-signed URL can never succeed.
        self.http_mocker.assert_number_of_calls(download_request, 1)


class TestBulkExpiredDownloadLink(ExpiredDownloadLinkMixin, test_bulk_stream.TestBulkStream):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def test_expired_bulk_download_link_fails_as_transient_error(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()

        output = self.read_with_expired_download_link(download_request, self._config)

        self.assert_fails_as_transient_expired_link(output, download_request)


class TestReportExpiredDownloadLink(ExpiredDownloadLinkMixin, BaseTest):
    stream_name = "ad_performance_report_hourly"

    @freeze_time("2024-05-06")
    def test_expired_report_download_link_fails_as_transient_error(self):
        test_hourly_reports.TestAdPerformanceReportHourlyStream.mock_report_apis(self)
        download_request = RequestBuilder(resource="").build_report_url()
        config = ConfigBuilder().with_reports_start_date("2024-01-01").build()

        output = self.read_with_expired_download_link(download_request, config)

        self.assert_fails_as_transient_expired_link(output, download_request)
