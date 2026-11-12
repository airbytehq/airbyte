# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Expired Azure Blob SAS download URLs (HTTP 403 AuthenticationFailed) must surface as a transient error.

The download URLs returned by the Bing Ads Reporting (``ReportDownloadUrl``) and Bulk (``ResultFileUrl``) APIs are
pre-signed Azure Blob Storage SAS URLs that expire shortly after being issued. When a download starts after expiry,
Azure answers 403 ``AuthenticationFailed`` / ``Signature not valid in the specified time frame``. This is not a user
permission problem, so it must not be reported as a ``config_error`` telling the user they lack permission.
"""

import test_bulk_stream
import test_hourly_reports
from base_test import BaseTest
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


AZURE_SAS_EXPIRED_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed "
    "correctly including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\n"
    "Time:2024-05-06T10:15:00.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Mon, 06 May 2024 09:55:00 GMT]"
    " - Expiry [Mon, 06 May 2024 10:05:00 GMT] - Current [Mon, 06 May 2024 10:15:00 GMT]</AuthenticationErrorDetail></Error>"
)


def _assert_expired_download_url_error(output, stream_name: str) -> None:
    assert not output.records
    trace_errors = [message.trace.error for message in output.errors]
    assert trace_errors, "expected the read to emit an error trace message"
    # The first trace is the per-stream error the platform surfaces. The CDK always appends a combined
    # "did not sync successfully" summary as config_error by design, so it is not asserted here.
    stream_error = trace_errors[0]
    assert (stream_error.failure_type, stream_error.message) == (
        FailureType.transient_error,
        f"The Bing Ads download link for stream '{stream_name}' expired before the file could be downloaded. The sync will retry.",
    )
    assert not any("You don't have permission" in (error.message or "") for error in trace_errors)


class TestReportExpiredDownloadUrl(BaseTest):
    stream_name = "age_gender_audience_report_hourly"

    @freeze_time("2024-05-06")
    def test_expired_report_download_url_is_transient_error(self):
        test_hourly_reports.TestAgeGenderAudienceReportHourlyStream.mock_report_apis(self)
        self.http_mocker.get(
            RequestBuilder(resource="").build_report_url(),
            HttpResponse(AZURE_SAS_EXPIRED_BODY, 403),
        )
        config = test_hourly_reports.TestAgeGenderAudienceReportHourlyStream()._config
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()

        output = read_helper(config, catalog, expecting_exception=True)

        _assert_expired_download_url_error(output, self.stream_name)


class TestBulkExpiredDownloadUrl(test_bulk_stream.TestBulkStream):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def test_expired_bulk_download_url_is_transient_error(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        self.http_mocker.get(
            RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build(),
            HttpResponse(AZURE_SAS_EXPIRED_BODY, 403),
        )
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()

        output = read_helper(self._config, catalog, expecting_exception=True)

        _assert_expired_download_url_error(output, self.stream_name)
