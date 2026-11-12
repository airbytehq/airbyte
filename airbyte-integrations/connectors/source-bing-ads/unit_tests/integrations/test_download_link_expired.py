# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""Download requests to Azure Blob Storage use pre-signed (SAS) URLs returned by the Bing Ads
Bulk/Reporting APIs. When such a URL expires, Azure answers 403 AuthenticationFailed. That must be
surfaced as a transient error naming the stream, not as the CDK's generic 403 permission config error.
"""

from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import REPORT_URL, RequestBuilder
from test_bulk_stream import TestBulkStream
from test_report_stream import TestReportStream

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


_AZURE_SAS_EXPIRED_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed "
    "correctly including the signature.</Message><AuthenticationErrorDetail>Signature not valid in the specified "
    "time frame: Start [Mon, 09 Nov 2026 10:00:00 GMT] - Expiry [Mon, 09 Nov 2026 10:10:00 GMT] - Current "
    "[Mon, 09 Nov 2026 10:30:00 GMT]</AuthenticationErrorDetail></Error>"
)

_SUBMIT_BODY = b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductSearchQueryPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductSearchQueryPerformanceReportRequest", "Aggregation": "Daily", "Columns": ["TimePeriod", "AccountId", "AccountNumber", "AccountName", "AdId", "AdGroupId", "AdGroupName", "CampaignId", "CampaignName", "DestinationUrl", "DeviceType", "DeviceOS", "Language", "SearchQuery", "Network", "MerchantProductId", "Title", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "AdGroupCriterionId", "ProductGroup", "PartitionType", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Assists", "CostPerAssist", "Revenue", "CostPerConversion", "RevenuePerConversion", "RevenuePerAssist", "CustomerId", "CustomerName", "AssistedImpressions", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllRevenuePerConversion", "Goal", "GoalType", "AbsoluteTopImpressionRatePercent", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "AllConversionsQualified", "CampaignType", "AssetGroupId", "AssetGroupName"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}'


def _azure_sas_expired_response() -> HttpResponse:
    return HttpResponse(
        _AZURE_SAS_EXPIRED_BODY,
        403,
        headers={"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"},
    )


def _assert_expired_link_error(output, stream_name: str) -> None:
    assert not output.records
    trace_errors = [m.trace.error for m in output.errors]
    assert trace_errors, "expected an error trace message"
    expected = f"The Bing Ads download link for stream '{stream_name}' expired before the file could be downloaded. The sync will retry."
    stream_errors = [e for e in trace_errors if e.message == expected]
    assert stream_errors, f"expected message {expected!r}, got {[e.message for e in trace_errors]}"
    assert all(e.failure_type == FailureType.transient_error for e in stream_errors)
    assert not any("You don't have permission" in (e.message or "") for e in trace_errors)


class TestBulkDownloadLinkExpired(TestBulkStream):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def test_expired_bulk_download_link_is_transient_error_naming_stream(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        self.http_mocker.get(
            RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build(),
            _azure_sas_expired_response(),
        )

        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        output = read_helper(self._config, catalog, None, expecting_exception=True)

        _assert_expired_link_error(output, self.stream_name)


class TestReportDownloadLinkExpired(TestReportStream):
    stream_name = "product_search_query_performance_report_daily"

    @freeze_time("2024-05-06")
    def test_expired_report_download_link_is_transient_error_naming_stream(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_generate_report_api(endpoint="Submit", response_template="generate_report", body=_SUBMIT_BODY)
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )
        self.http_mocker.get(HttpRequest(url=REPORT_URL), _azure_sas_expired_response())

        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        output = read_helper(self._config, catalog, None, expecting_exception=True)

        _assert_expired_link_error(output, self.stream_name)
