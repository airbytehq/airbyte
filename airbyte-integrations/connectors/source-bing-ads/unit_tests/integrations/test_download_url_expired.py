# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""Download failures caused by an expired Azure Blob SAS link (403 AuthenticationFailed)."""

from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from test_bulk_stream import TestBulkStream

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed "
    "correctly including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\nTime:2024-05-06T00:00:00.0000000Z"
    "</Message><AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Mon, 06 May 2024 "
    "00:00:00 GMT] - Expiry [Mon, 06 May 2024 00:10:00 GMT] - Current [Mon, 06 May 2024 00:20:00 GMT]"
    "</AuthenticationErrorDetail></Error>"
)
ACCOUNTS_SEARCH_BODY = b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}'
# Submit body of product_dimension_performance_report_daily for 2024-01-01..2024-05-06
PRODUCT_DIMENSION_DAILY_SUBMIT_BODY = b'{"ReportRequest": {"ExcludeColumnHeaders": false, "ExcludeReportFooter": true, "ExcludeReportHeader": true, "Format": "Csv", "FormatVersion": "2.0", "ReportName": "ProductDimensionPerformanceReport", "ReturnOnlyCompleteData": false, "Type": "ProductDimensionPerformanceReportRequest", "Aggregation": "Daily", "Columns": ["TimePeriod", "AccountName", "AccountNumber", "AdGroupName", "AdGroupId", "CampaignStatus", "AccountStatus", "AdGroupStatus", "Network", "AdId", "CampaignId", "CampaignName", "CurrencyCode", "DeviceType", "Language", "MerchantProductId", "Title", "Condition", "Brand", "Price", "Impressions", "Clicks", "Ctr", "AverageCpc", "Spend", "Conversions", "ConversionRate", "Revenue", "RevenuePerConversion", "SellerName", "OfferLanguage", "CountryOfSale", "AdStatus", "AdDistribution", "ClickTypeId", "TotalClicksOnAdElements", "ClickType", "ReturnOnAdSpend", "BidStrategyType", "LocalStoreCode", "StoreId", "AssistedClicks", "AssistedConversions", "AllConversions", "AllRevenue", "AllConversionRate", "AllCostPerConversion", "AllReturnOnAdSpend", "AllRevenuePerConversion", "CostPerConversion", "ViewThroughConversions", "Goal", "GoalType", "ProductBought", "QuantityBought", "AverageCpm", "ConversionsQualified", "AssistedConversionsQualified", "ViewThroughConversionsQualified", "ProductBoughtTitle", "GTIN", "MPN", "ViewThroughRevenue", "Sales", "CostPerSale", "RevenuePerSale", "Installs", "CostPerInstall", "RevenuePerInstall", "CampaignType", "AssetGroupId", "AssetGroupName", "AssetGroupStatus", "CustomLabel0", "CustomLabel1", "CustomLabel2", "CustomLabel3", "CustomLabel4", "ProductType1", "ProductType2", "ProductType3", "ProductType4", "ProductType5"], "Scope": {"AccountIds": [180535609]}, "Time": {"CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024}, "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024}, "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon"}}}'
EXPIRED_SAS_HEADERS = {"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"}


def _expired_sas_response() -> HttpResponse:
    return HttpResponse(EXPIRED_SAS_BODY, 403, EXPIRED_SAS_HEADERS)


def _assert_expired_download_error(output, stream_name: str) -> None:
    assert not output.records
    # The CDK always ends a failed concurrent read with a generic config_error summary
    # ("During the sync, the following streams did not sync successfully"); the per-stream
    # trace emitted before it is the one the platform surfaces to the user.
    stream_errors = [e.trace.error for e in output.errors if e.trace.error.internal_message != "Concurrent read failure"]
    assert len(stream_errors) == 1
    error = stream_errors[0]
    assert error.failure_type == FailureType.transient_error
    assert error.message == (
        f"The Bing Ads download link for stream '{stream_name}' expired before the file could be downloaded. The sync will retry."
    )


class TestBulkDownloadUrlExpired(TestBulkStream):
    stream_name = "app_install_ads"
    download_entity = "AppInstallAds"

    def test_expired_bulk_download_url_raises_transient_error(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=ACCOUNTS_SEARCH_BODY,
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()
        download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        self.http_mocker.get(download_request, _expired_sas_response())

        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        output = read_helper(self._config, catalog, expecting_exception=True)

        _assert_expired_download_error(output, self.stream_name)
        # Re-requesting the same expired URL cannot succeed, so the download is not retried in-process.
        self.http_mocker.assert_number_of_calls(download_request, 1)


class TestReportDownloadUrlExpired(BaseTest):
    stream_name = "product_dimension_performance_report_daily"

    @property
    def _config(self) -> dict:
        return ConfigBuilder().with_reports_start_date("2024-01-01").build()

    @freeze_time("2024-05-06")
    def test_expired_report_download_url_raises_transient_error(self):
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(response_template="accounts_search_for_report", body=ACCOUNTS_SEARCH_BODY)
        self.mock_generate_report_api(endpoint="Submit", response_template="generate_report", body=PRODUCT_DIMENSION_DAILY_SUBMIT_BODY)
        # Both the AsyncRetriever poll and the requester's pre-download re-poll hit this endpoint.
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )
        download_request = RequestBuilder(resource="").build_report_url()
        self.http_mocker.get(download_request, _expired_sas_response())

        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        output = read_helper(self._config, catalog, expecting_exception=True)

        _assert_expired_download_error(output, self.stream_name)
        self.http_mocker.assert_number_of_calls(download_request, 1)
