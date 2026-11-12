# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json

from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from protocol_helpers import read_helper


_EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nTime:2026-01-01T20:23:43.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Thu, 01 Jan 2026 19:41:55 GMT] - "
    "Expiry [Thu, 01 Jan 2026 20:06:55 GMT] - Current [Thu, 01 Jan 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
_EXPIRED_SAS_HEADERS = {"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"}
_EXPECTED_MESSAGE = "Bing Ads file download URL is expired."
_ACCOUNTS_SEARCH_BODY = (
    b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], '
    b'"ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
)
_BULK_SUBMIT_BODY = (
    '{"AccountIds": ["180535609"], "DataScope": "EntityData", "DownloadEntities": ["Budgets"], '
    '"DownloadFileType": "Csv", "FormatVersion": "6.0", "CompressionType": "GZip"}'
)
_REPORT_SUBMIT_BODY = b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "AgeGenderAudienceReport", "ReturnOnlyCompleteData": false, "Type": "AgeGenderAudienceReportRequest", "Aggregation": "Hourly", "Columns": ["AccountName", "AccountNumber", "AccountId", "TimePeriod", "CampaignName", "CampaignId", "AdGroupName", "AdGroupId", "AdDistribution", "AgeGroup", "Gender", "Impressions", "Clicks", "Conversions", "Spend", "Revenue", "ExtendedCost", "Assists", "Language", "AccountStatus", "CampaignStatus", "AdGroupStatus", "BaseCampaignId", "AllConversions", "AllRevenue", "ViewThroughConversions", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "TopImpressionRatePercent", "ConversionsQualified", "AllConversionsQualified", "ViewThroughConversionsQualified", "ViewThroughRevenue"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}'
_BULK_DOWNLOAD_URL = "https://bulk.api.bingads.microsoft.com/path/to/bulk/resultquery/url"


class TestDownloadUrlExpired(BaseTest):
    """An expired Azure SAS download URL (403 AuthenticationFailed) must surface as a transient error, not a permission/config error."""

    def _mock_accounts(self) -> None:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(response_template="accounts_search_for_report", body=_ACCOUNTS_SEARCH_BODY)

    def _assert_expired_url_error(self, output, download_url: str) -> None:
        errors = [message.trace.error for message in output.errors]
        assert errors, "expected the sync to emit an error trace"
        expired_errors = [error for error in errors if error.message == _EXPECTED_MESSAGE]
        assert expired_errors, f"expected '{_EXPECTED_MESSAGE}', got {[error.message for error in errors]}"
        assert all(error.failure_type == FailureType.transient_error for error in expired_errors)
        assert not any("You don't have permission" in (error.message or "") for error in errors)
        assert all(download_url in (error.internal_message or "") for error in expired_errors)

    def test_bulk_stream_expired_download_url_is_transient_error(self) -> None:
        self._mock_accounts()
        self.http_mocker.post(
            RequestBuilder(resource="Bulk/v13/Campaigns/DownloadByAccountIds", api="bulk").with_body(_BULK_SUBMIT_BODY).build(),
            HttpResponse(json.dumps(find_template(resource="bulk_download", execution_folder=__file__)), 200),
        )
        self.http_mocker.post(
            RequestBuilder(resource="Bulk/v13/BulkDownloadStatus/Query", api="bulk").with_body('{"RequestId": "TestDownloadRequestId"}').build(),
            HttpResponse(json.dumps(find_template(resource="bulk_status", execution_folder=__file__)), 200),
        )
        self.http_mocker.get(HttpRequest(url=_BULK_DOWNLOAD_URL), HttpResponse(_EXPIRED_SAS_BODY, 403, _EXPIRED_SAS_HEADERS))

        catalog = CatalogBuilder().with_stream("budget", SyncMode.full_refresh).build()
        output = read_helper(self._config, catalog, None, expecting_exception=True)

        assert len(output.records) == 0
        self._assert_expired_url_error(output, _BULK_DOWNLOAD_URL)

    @freeze_time("2024-05-06")
    def test_report_stream_expired_download_url_is_transient_error(self) -> None:
        self._mock_accounts()
        self.http_mocker.post(
            RequestBuilder(resource="GenerateReport/Submit", api="reporting").with_body(_REPORT_SUBMIT_BODY).build(),
            HttpResponse(json.dumps(find_template(resource="generate_report", execution_folder=__file__)), 200),
        )
        self.http_mocker.post(
            RequestBuilder(resource="GenerateReport/Poll", api="reporting").with_body(b'{"ReportRequestId": "thisisthereport_requestid"}').build(),
            HttpResponse(json.dumps(find_template(resource="generate_report_poll", execution_folder=__file__)), 200),
        )
        self.http_mocker.get(RequestBuilder().build_report_url(), HttpResponse(_EXPIRED_SAS_BODY, 403, _EXPIRED_SAS_HEADERS))

        catalog = CatalogBuilder().with_stream("age_gender_audience_report_hourly", SyncMode.full_refresh).build()
        output = read_helper(ConfigBuilder().with_reports_start_date("2024-01-01").build(), catalog, None, expecting_exception=True)

        assert len(output.records) == 0
        self._assert_expired_url_error(output, "https://bingadsappsstorageprod.blob.core.windows.net")

    def test_bulk_stream_other_403_keeps_default_classification(self) -> None:
        self._mock_accounts()
        self.http_mocker.post(
            RequestBuilder(resource="Bulk/v13/Campaigns/DownloadByAccountIds", api="bulk").with_body(_BULK_SUBMIT_BODY).build(),
            HttpResponse(json.dumps(find_template(resource="bulk_download", execution_folder=__file__)), 200),
        )
        self.http_mocker.post(
            RequestBuilder(resource="Bulk/v13/BulkDownloadStatus/Query", api="bulk").with_body('{"RequestId": "TestDownloadRequestId"}').build(),
            HttpResponse(json.dumps(find_template(resource="bulk_status", execution_folder=__file__)), 200),
        )
        self.http_mocker.get(
            HttpRequest(url=_BULK_DOWNLOAD_URL),
            HttpResponse('<?xml version="1.0"?><Error><Code>AuthorizationFailure</Code></Error>', 403, {"x-ms-error-code": "AuthorizationFailure"}),
        )

        catalog = CatalogBuilder().with_stream("budget", SyncMode.full_refresh).build()
        output = read_helper(self._config, catalog, None, expecting_exception=True)

        errors = [message.trace.error for message in output.errors]
        assert not any(error.message == _EXPECTED_MESSAGE for error in errors)
        assert any(error.failure_type == FailureType.config_error for error in errors)
