# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""Reads where Azure Blob Storage rejects the pre-signed (SAS) download URL because it expired."""

from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from test_bulk_stream import TestBulkStream

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


ACCOUNTS_SEARCH_BODY = (
    b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], '
    b'"ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
)

# Response body Azure Blob Storage returns for a SAS URL used outside of its validity window.
SAS_EXPIRED_BODY = (
    '﻿<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\nTime:2026-11-12T10:00:00.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Thu, 12 Nov 2026 09:00:00 GMT] - "
    "Expiry [Thu, 12 Nov 2026 09:10:00 GMT] - Current [Thu, 12 Nov 2026 10:00:00 GMT]</AuthenticationErrorDetail></Error>"
)


def _sas_expired_response() -> HttpResponse:
    return HttpResponse(SAS_EXPIRED_BODY, 403, headers={"Content-Type": "application/xml"})


def _assert_download_link_expired_error(output, stream_name: str) -> None:
    assert not output.records
    stream_errors = [error.trace.error for error in output.errors if error.trace.error.stream_descriptor]
    assert len(stream_errors) == 1
    trace = stream_errors[0]
    assert trace.stream_descriptor.name == stream_name
    assert trace.failure_type == FailureType.transient_error
    assert trace.message == (
        f"The Bing Ads download link for stream '{stream_name}' expired before the file could be downloaded. The sync will retry."
    )


class TestBulkStreamDownloadLinkExpired(TestBulkStream):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def test_expired_sas_url_fails_as_transient_error_with_stream_name(self) -> None:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(response_template="accounts_search_for_report", body=ACCOUNTS_SEARCH_BODY)
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        self.http_mocker.get(download_request, _sas_expired_response())

        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        output = read_helper(self._config, catalog, expecting_exception=True)

        _assert_download_link_expired_error(output, self.stream_name)
        # The stale URL is not retried: it cannot become valid again.
        self.http_mocker.assert_number_of_calls(download_request, 1)


class TestReportStreamDownloadLinkExpired(BaseTest):
    stream_name = "product_search_query_performance_report_daily"

    @freeze_time("2024-05-06")
    def test_expired_sas_url_fails_as_transient_error_with_stream_name(self) -> None:
        # Imported here so pytest does not collect the whole report suite a second time from this module.
        from test_product_search_query_performance_report import TestProductSearchQueryPerformanceReportDailyStream

        config = ConfigBuilder().with_reports_start_date("2024-01-01").build()
        # Reuse that suite's mocks for the user/accounts lookup and the GenerateReport Submit and Poll requests.
        report_suite = TestProductSearchQueryPerformanceReportDailyStream()
        report_suite._http_mocker = self.http_mocker
        report_suite.mock_report_apis()
        download_request = RequestBuilder(resource="").build_report_url()
        self.http_mocker.get(download_request, _sas_expired_response())

        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        output = read_helper(config, catalog, expecting_exception=True)

        _assert_download_link_expired_error(output, self.stream_name)
        self.http_mocker.assert_number_of_calls(download_request, 1)
