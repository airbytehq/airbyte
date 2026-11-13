# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json

from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


ACCOUNTS_SEARCH_BODY = b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
BULK_DOWNLOAD_REQUEST_BODY = (
    '{"AccountIds": ["180535609"], "DataScope": "EntityData", "DownloadEntities": ["Budgets"], '
    '"DownloadFileType": "Csv", "FormatVersion": "6.0", "CompressionType": "GZip"}'
)
REPORT_STREAM = "product_dimension_performance_report_daily"
REPORT_SUBMIT_BODY = b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Daily", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}'
BULK_DOWNLOAD_URL = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
REPORT_DOWNLOAD_URL = RequestBuilder(resource="").build_report_url()

# Azure Blob Storage response when the pre-signed (SAS) download URL handed out by Bing Ads has expired.
EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.</Message><AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [Mon, 06 May 2024 00:00:00 GMT] - Expiry [Mon, 06 May 2024 00:10:00 GMT] - Current [Mon, 06 May 2024 00:20:00 GMT]"
    "</AuthenticationErrorDetail></Error>"
)
EXPIRED_SAS_HEADERS = {"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"}
EXPECTED_MESSAGE = (
    "The Bing Ads file download link expired before the file could be downloaded (HTTP 403 from Azure Blob Storage). "
    "This is a temporary error, not a permissions issue, and the sync will retry."
)


class TestExpiredDownloadUrl(BaseTest):
    start_date = "2024-01-01"
    """A 403 from an expired SAS download URL must be a transient error, not a 'you lack permission' config error."""

    @property
    def _config(self) -> dict:
        return ConfigBuilder().with_reports_start_date(self.start_date).build()

    def _mock_accounts(self) -> None:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(response_template="accounts_search_for_report", body=ACCOUNTS_SEARCH_BODY)

    def _mock_bulk_job(self) -> None:
        self.http_mocker.post(
            RequestBuilder(resource="Bulk/v13/Campaigns/DownloadByAccountIds", api="bulk").with_body(BULK_DOWNLOAD_REQUEST_BODY).build(),
            HttpResponse(json.dumps(find_template(resource="bulk_download", execution_folder=__file__)), 200),
        )
        self.http_mocker.post(
            RequestBuilder(resource="Bulk/v13/BulkDownloadStatus/Query", api="bulk").with_body('{"RequestId": "TestDownloadRequestId"}').build(),
            HttpResponse(json.dumps(find_template(resource="bulk_status", execution_folder=__file__)), 200),
        )

    def _mock_report_job(self) -> None:
        self.mock_generate_report_api(endpoint="Submit", response_template="generate_report", body=REPORT_SUBMIT_BODY)
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )

    def _read_with_expired_download(self, stream_name: str, download_request: HttpRequest) -> EntrypointOutput:
        self.http_mocker.get(download_request, HttpResponse(EXPIRED_SAS_BODY, 403, headers=EXPIRED_SAS_HEADERS))
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, expecting_exception=True)

    def _assert_transient_expired_link_error(self, output: EntrypointOutput, stream_name: str, download_request: HttpRequest) -> None:
        assert output.records == []
        stream_errors = [message.trace.error for message in output.errors if message.trace.error.stream_descriptor]
        assert [(error.stream_descriptor.name, error.failure_type, error.message) for error in stream_errors] == [
            (stream_name, FailureType.transient_error, EXPECTED_MESSAGE)
        ]
        # The stale URL is not retried in place; the platform retries the attempt with a fresh job instead.
        self.http_mocker.assert_number_of_calls(download_request, 1)

    def test_bulk_stream_expired_download_url_is_transient_error(self):
        self._mock_accounts()
        self._mock_bulk_job()
        output = self._read_with_expired_download("budget", BULK_DOWNLOAD_URL)
        self._assert_transient_expired_link_error(output, "budget", BULK_DOWNLOAD_URL)

    @freeze_time("2024-05-06")
    def test_report_stream_expired_download_url_is_transient_error(self):
        self._mock_accounts()
        self._mock_report_job()
        output = self._read_with_expired_download(REPORT_STREAM, REPORT_DOWNLOAD_URL)
        self._assert_transient_expired_link_error(output, REPORT_STREAM, REPORT_DOWNLOAD_URL)
