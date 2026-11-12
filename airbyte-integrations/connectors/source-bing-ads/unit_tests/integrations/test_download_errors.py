# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import test_hourly_reports
from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from test_bulk_stream import TestBulkStream

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\nTime:2026-11-10T20:23:43.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Tue, 10 Nov 2026 19:41:55 GMT] - "
    "Expiry [Tue, 10 Nov 2026 20:06:55 GMT] - Current [Tue, 10 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
PERMISSION_MISMATCH_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationPermissionMismatch</Code>'
    "<Message>This request is not authorized to perform this operation using this permission.\n"
    "RequestId:00000000-0000-0000-0000-000000000000\nTime:2026-11-10T20:23:43.0000000Z</Message></Error>"
)
EXPIRED_URL_MESSAGE = "Bing Ads file download URL is expired."
DEFAULT_FORBIDDEN_MESSAGE = "Forbidden. You don't have permission to access this resource."


class _DownloadErrorContract:
    """Read contracts for 403 responses from the Azure Blob Storage file download URL."""

    stream_name: str

    def mock_job_apis(self) -> None:
        raise NotImplementedError

    def download_request(self) -> HttpRequest:
        raise NotImplementedError

    def _read_with_download_error(self, body: str, azure_error_code: str):
        self.mock_job_apis()
        self.http_mocker.get(
            self.download_request(),
            HttpResponse(body, 403, headers={"Content-Type": "application/xml", "x-ms-error-code": azure_error_code}),
        )
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, expecting_exception=True)

    def _stream_failure(self, output):
        traces = [error.trace.error for error in output.errors if error.trace.error.stream_descriptor]
        assert len(traces) == 1, traces
        assert traces[0].stream_descriptor.name == self.stream_name
        return traces[0]

    def test_expired_download_url_fails_as_transient_error(self):
        output = self._read_with_download_error(EXPIRED_SAS_BODY, "AuthenticationFailed")

        failure = self._stream_failure(output)
        assert failure.failure_type == FailureType.transient_error
        assert failure.message == EXPIRED_URL_MESSAGE
        assert "Signature not valid in the specified time frame" in failure.internal_message
        assert output.records == []

    def test_other_forbidden_download_keeps_config_error(self):
        output = self._read_with_download_error(PERMISSION_MISMATCH_BODY, "AuthorizationPermissionMismatch")

        failure = self._stream_failure(output)
        assert failure.failure_type == FailureType.config_error
        assert failure.message == DEFAULT_FORBIDDEN_MESSAGE
        assert output.records == []


class TestBulkDownloadErrors(_DownloadErrorContract, TestBulkStream):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def mock_job_apis(self) -> None:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()

    def download_request(self) -> HttpRequest:
        return RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()


@freeze_time("2024-05-06")
class TestReportDownloadErrors(_DownloadErrorContract, BaseTest):
    stream_name = "age_gender_audience_report_hourly"

    @property
    def _config(self):
        return ConfigBuilder().with_reports_start_date("2024-01-01").build()

    def mock_job_apis(self) -> None:
        test_hourly_reports.TestAgeGenderAudienceReportHourlyStream.mock_report_apis(self)

    def download_request(self) -> HttpRequest:
        return RequestBuilder(resource="").build_report_url()
