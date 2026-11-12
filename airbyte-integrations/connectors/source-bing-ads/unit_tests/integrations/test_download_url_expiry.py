# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""
Bing Ads returns pre-signed Azure Blob Storage SAS URLs for bulk and report file downloads.
When such a URL expires before the download starts, Azure answers with
`403 AuthenticationFailed - Signature not valid in the specified time frame`.
That is not a permission problem: the sync must report it as a transient error with a specific message.
"""

from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from test_bulk_stream import TestBulkStream
from test_report_stream import TestReportStream

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:a1b2c3d4-0001-0002-0003-000000000000\nTime:2026-11-10T20:23:43.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Tue, 10 Nov 2026 19:41:55 GMT] - "
    "Expiry [Tue, 10 Nov 2026 20:06:55 GMT] - Current [Tue, 10 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
EXPIRED_SAS_RESPONSE_HEADERS = {"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"}
PRODUCT_SEARCH_QUERY_DAILY_SUBMIT_BODY = b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductSearchQueryPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductSearchQueryPerformanceReportRequest", "Aggregation": "Daily", "Columns": ["TimePeriod", "AccountId", "AccountNumber", "AccountName", "AdId", "AdGroupId", "AdGroupName", "CampaignId", "CampaignName", "DestinationUrl", "DeviceType", "DeviceOS", "Language", "SearchQuery", "Network", "MerchantProductId", "Title", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "AdGroupCriterionId", "ProductGroup", "PartitionType", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Assists", "CostPerAssist", "Revenue", "CostPerConversion", "RevenuePerConversion", "RevenuePerAssist", "CustomerId", "CustomerName", "AssistedImpressions", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllRevenuePerConversion", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "AllConversionsQualified", "CampaignType", "AssetGroupId", "AssetGroupName"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}'
BULK_DOWNLOAD_REQUEST = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
REPORT_DOWNLOAD_REQUEST = RequestBuilder(resource="").build_report_url()
EXPECTED_MESSAGE = "Bing Ads file download URL is expired."


def _assert_expired_url_error(output, stream_name: str) -> None:
    assert not output.records
    trace_errors = [message.trace.error for message in output.errors]
    assert trace_errors, "expected an error trace message"
    stream_errors = [error for error in trace_errors if error.stream_descriptor and error.stream_descriptor.name == stream_name]
    assert stream_errors, f"expected an error trace for stream {stream_name}, got {trace_errors}"
    for error in stream_errors:
        assert error.message == EXPECTED_MESSAGE
        assert error.failure_type == FailureType.transient_error
        assert "Signature not valid in the specified time frame" in error.internal_message


class TestBulkDownloadUrlExpiry(TestBulkStream):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def _mock_bulk_apis_with_download_response(self, download_response: HttpResponse) -> None:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        self.http_mocker.get(BULK_DOWNLOAD_REQUEST, download_response)

    def _read(self):
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, expecting_exception=True)

    def test_expired_sas_download_url_is_reported_as_transient_error(self):
        self._mock_bulk_apis_with_download_response(HttpResponse(EXPIRED_SAS_BODY, 403, EXPIRED_SAS_RESPONSE_HEADERS))

        output = self._read()

        _assert_expired_url_error(output, self.stream_name)
        # Retrying would resend the same expired URL, so the download is attempted exactly once.
        self.http_mocker.assert_number_of_calls(BULK_DOWNLOAD_REQUEST, 1)

    def test_other_forbidden_download_response_keeps_config_error(self):
        self._mock_bulk_apis_with_download_response(
            HttpResponse(
                '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationPermissionMismatch</Code>'
                "<Message>This request is not authorized to perform this operation using this permission.</Message></Error>",
                403,
                {"Content-Type": "application/xml", "x-ms-error-code": "AuthorizationPermissionMismatch"},
            )
        )

        output = self._read()

        trace_errors = [message.trace.error for message in output.errors if message.trace.error.stream_descriptor]
        assert trace_errors
        for error in trace_errors:
            assert error.message != EXPECTED_MESSAGE
            assert error.failure_type == FailureType.config_error


class TestReportDownloadUrlExpiry(TestReportStream):
    stream_name = "product_search_query_performance_report_daily"

    def _mock_report_apis(self) -> None:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_generate_report_api(endpoint="Submit", response_template="generate_report", body=PRODUCT_SEARCH_QUERY_DAILY_SUBMIT_BODY)
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )

    @freeze_time("2024-05-06")
    def test_expired_sas_report_download_url_is_reported_as_transient_error(self):
        self._mock_report_apis()
        self.http_mocker.get(REPORT_DOWNLOAD_REQUEST, HttpResponse(EXPIRED_SAS_BODY, 403, EXPIRED_SAS_RESPONSE_HEADERS))
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()

        output = read_helper(self._config, catalog, expecting_exception=True)

        _assert_expired_url_error(output, self.stream_name)
        self.http_mocker.assert_number_of_calls(REPORT_DOWNLOAD_REQUEST, 1)
