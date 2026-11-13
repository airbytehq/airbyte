# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""
Bing Ads hands out pre-signed Azure Blob URLs for bulk and report files. When one expires before the file is
downloaded, Azure answers 403 with `x-ms-error-code: AuthenticationFailed`. That must be reported as an expired
download URL (transient), not as a permission problem (config error).
"""

from typing import Any, Mapping, Optional

import test_hourly_reports
from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from test_bulk_stream import TestBulkStream

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_DOWNLOAD_URL_MESSAGE = "Bing Ads file download URL is expired or no longer valid."

AZURE_SAS_EXPIRED_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed "
    "correctly including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\n"
    "Time:2026-11-01T20:23:43.0000000Z</Message><AuthenticationErrorDetail>Signature not valid in the specified "
    "time frame: Start [Sun, 01 Nov 2026 19:41:55 GMT] - Expiry [Sun, 01 Nov 2026 20:06:55 GMT] - "
    "Current [Sun, 01 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
AZURE_SAS_EXPIRED_HEADERS = {"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"}


def _expired_sas_response() -> HttpResponse:
    return HttpResponse(AZURE_SAS_EXPIRED_BODY, 403, AZURE_SAS_EXPIRED_HEADERS)


def _stream_error(output: EntrypointOutput, stream_name: str):
    assert not output.records
    stream_errors = [
        message.trace.error
        for message in output.errors
        if message.trace.error.stream_descriptor and message.trace.error.stream_descriptor.name == stream_name
    ]
    assert len(stream_errors) == 1, output.errors
    return stream_errors[0]


class TestBulkDownloadUrlExpired(TestBulkStream):
    stream_name = "budget"
    download_entity = "Budgets"

    def _mock_apis_with_download_response(self, download_response: HttpResponse) -> None:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        self._download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        self.http_mocker.get(self._download_request, download_response)

    def _read(self) -> EntrypointOutput:
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, None, expecting_exception=True)

    def test_expired_download_url_is_reported_as_transient_error(self):
        self._mock_apis_with_download_response(_expired_sas_response())

        error = _stream_error(self._read(), self.stream_name)

        assert error.failure_type == FailureType.transient_error
        assert error.message == EXPIRED_DOWNLOAD_URL_MESSAGE
        assert "Signature not valid in the specified time frame" in error.internal_message
        self.http_mocker.assert_number_of_calls(self._download_request, 1)


class TestReportDownloadUrlExpired(BaseTest):
    stream_name = "age_gender_audience_report_hourly"
    mock_report_apis = test_hourly_reports.TestAgeGenderAudienceReportHourlyStream.mock_report_apis

    @property
    def _config(self) -> Mapping[str, Any]:
        return ConfigBuilder().with_reports_start_date("2024-01-01").build()

    def _read(self, download_response: HttpResponse) -> EntrypointOutput:
        self.mock_report_apis()
        self._download_request = RequestBuilder(resource="").build_report_url()
        self.http_mocker.get(self._download_request, download_response)
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, None, expecting_exception=True)

    @freeze_time("2024-05-06")
    def test_expired_download_url_is_reported_as_transient_error(self):
        error = _stream_error(self._read(_expired_sas_response()), self.stream_name)

        assert error.failure_type == FailureType.transient_error
        assert error.message == EXPIRED_DOWNLOAD_URL_MESSAGE
        self.http_mocker.assert_number_of_calls(self._download_request, 1)
