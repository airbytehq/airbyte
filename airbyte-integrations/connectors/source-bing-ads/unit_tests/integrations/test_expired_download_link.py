# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import test_hourly_reports
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from test_bulk_stream import TestBulkStream

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


# Body and header Azure Blob Storage returns for a pre-signed (SAS) URL used outside its validity window.
EXPIRED_SAS_RESPONSE = HttpResponse(
    body=(
        '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
        "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
        "including the signature.\nRequestId:11111111-2222-3333-4444-555555555555\nTime:2024-05-06T00:20:00.0000000Z</Message>"
        "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Mon, 06 May 2024 00:00:00 GMT] - "
        "Expiry [Mon, 06 May 2024 00:10:00 GMT] - Current [Mon, 06 May 2024 00:20:00 GMT]</AuthenticationErrorDetail></Error>"
    ),
    status_code=403,
    headers={"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"},
)


class TestExpiredDownloadLink(TestBulkStream):
    download_entity = "AppInstallAds"

    def _assert_expired_link_error(self, stream_name: str, config: dict, download_request: HttpRequest) -> None:
        self.http_mocker.get(download_request, EXPIRED_SAS_RESPONSE)
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

        output = read_helper(config, catalog, expecting_exception=True)

        assert output.records == []
        # errors[1] is the CDK's end-of-sync summary of failed streams; errors[0] is the stream's own failure.
        error = output.errors[0].trace.error
        assert error.stream_descriptor.name == stream_name
        assert error.failure_type == FailureType.transient_error
        assert error.message == "Bing Ads rejected the file download link as expired or no longer valid."
        # An expired link never becomes valid again, so the download is not retried against the same URL.
        self.http_mocker.assert_number_of_calls(download_request, 1)

    def test_bulk_stream_reports_expired_download_link_as_transient_error(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        self._assert_expired_link_error(
            "app_install_ads",
            self._config,
            RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build(),
        )

    @freeze_time("2024-05-06")
    def test_report_stream_reports_expired_download_link_as_transient_error(self):
        test_hourly_reports.TestAccountImpressionPerformanceReportHourlyStream.mock_report_apis(self)
        self._assert_expired_link_error(
            "account_impression_performance_report_hourly",
            ConfigBuilder().with_reports_start_date("2024-01-01").build(),
            RequestBuilder(resource="").build_report_url(),
        )
