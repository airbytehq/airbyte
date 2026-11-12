# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""
Report and bulk files are downloaded from pre-signed Azure Blob (SAS) URLs returned by the Bing Ads Reporting/Bulk APIs.
A 403 on that download means Azure rejected the link (usually because it expired), not that the user lacks permission,
so it must surface as a transient error instead of the CDK's default "You don't have permission" config error.
"""

import json

from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import REPORT_URL, RequestBuilder
from test_bulk_stream import TestBulkStream

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


# Response Azure Blob Storage returns when the SAS download URL has expired.
_EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed "
    "correctly including the signature.\nRequestId:1f2e3d4c-0000-0000-0000-000000000000\nTime:2026-11-01T20:23:43.0000000Z"
    "</Message><AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [Sun, 01 Nov 2026 19:41:55 GMT] - Expiry [Sun, 01 Nov 2026 20:06:55 GMT] - "
    "Current [Sun, 01 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
_EXPIRED_SAS_HEADERS = {"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"}
_OTHER_FORBIDDEN_BODY = '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationFailure</Code></Error>'
_OTHER_FORBIDDEN_HEADERS = {"Content-Type": "application/xml", "x-ms-error-code": "AuthorizationFailure"}

_EXPIRED_MESSAGE = "Bing Ads file download URL is expired."
_REJECTED_MESSAGE = "Bing Ads file storage rejected the file download URL."

_ACCOUNTS_SEARCH_BODY = b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
_BULK_DOWNLOAD_URL = "https://bulk.api.bingads.microsoft.com/path/to/bulk/resultquery/url"
_AGE_GENDER_HOURLY_SUBMIT_BODY = (
    b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", '
    b'"FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", '
    b'"Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", '
    b'"AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", '
    b'"ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", '
    b'"AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", '
    b'"ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], '
    b'"Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, '
    b'"CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}'
)


class DownloadForbiddenContract:
    """Shared contract for every download requester. Subclasses mock the APIs that lead up to the download."""

    stream_name: str

    def _mock_apis_with_download_response(self, response: HttpResponse) -> HttpRequest:
        """Mock everything up to the file download and return the registered download request."""
        raise NotImplementedError

    def _read_expecting_failure(self):
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, None, True)

    def _assert_single_transient_failure(self, response: HttpResponse, expected_message: str, internal_detail: str) -> None:
        download_request = self._mock_apis_with_download_response(response)

        output = self._read_expecting_failure()

        assert output.records == []
        # The CDK also emits a sync-level "Concurrent read failure" trace without a stream descriptor; it wraps the
        # stream errors and is not the error this contract is about.
        stream_errors = [
            message.trace.error
            for message in output.errors
            if message.trace.error.stream_descriptor and message.trace.error.stream_descriptor.name == self.stream_name
        ]
        assert len(stream_errors) == 1
        assert stream_errors[0].failure_type == FailureType.transient_error
        assert stream_errors[0].message == expected_message
        assert internal_detail in stream_errors[0].internal_message
        # The same pre-signed URL would be rejected again, so it is requested only once.
        self.http_mocker.assert_number_of_calls(download_request, 1)

    @freeze_time("2024-05-06")
    def test_expired_download_url_fails_as_transient_error_with_specific_message(self):
        self._assert_single_transient_failure(
            HttpResponse(_EXPIRED_SAS_BODY, 403, _EXPIRED_SAS_HEADERS),
            _EXPIRED_MESSAGE,
            "Signature not valid in the specified time frame",
        )

    @freeze_time("2024-05-06")
    def test_other_forbidden_download_fails_as_transient_error_without_permission_message(self):
        self._assert_single_transient_failure(
            HttpResponse(_OTHER_FORBIDDEN_BODY, 403, _OTHER_FORBIDDEN_HEADERS),
            _REJECTED_MESSAGE,
            "AuthorizationFailure",
        )


class TestBulkStreamDownloadForbidden(DownloadForbiddenContract, TestBulkStream):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def _mock_apis_with_download_response(self, response: HttpResponse) -> HttpRequest:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(response_template="accounts_search_for_report", body=_ACCOUNTS_SEARCH_BODY)
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        download_request = HttpRequest(url=_BULK_DOWNLOAD_URL)
        self.http_mocker.get(download_request, response)
        return download_request


class TestReportStreamDownloadForbidden(DownloadForbiddenContract, BaseTest):
    stream_name = "age_gender_audience_report_hourly"

    @property
    def _config(self):
        return ConfigBuilder().with_reports_start_date("2024-01-01").build()

    def _mock_apis_with_download_response(self, response: HttpResponse) -> HttpRequest:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(response_template="accounts_search_for_report", body=_ACCOUNTS_SEARCH_BODY)
        self.http_mocker.post(
            RequestBuilder(resource="GenerateReport/Submit", api="reporting").with_body(_AGE_GENDER_HOURLY_SUBMIT_BODY).build(),
            HttpResponse(json.dumps(find_template(resource="generate_report", execution_folder=__file__)), 200),
        )
        # Answers both the async job poll and BingAdsReportDownloadRequester's re-poll for a fresh URL.
        self.http_mocker.post(
            RequestBuilder(resource="GenerateReport/Poll", api="reporting")
            .with_body(b'{"ReportRequestId": "thisisthereport_requestid"}')
            .build(),
            HttpResponse(json.dumps(find_template(resource="generate_report_poll", execution_folder=__file__)), 200),
        )
        download_request = HttpRequest(url=REPORT_URL)
        self.http_mocker.get(download_request, response)
        return download_request
