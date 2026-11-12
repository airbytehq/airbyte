# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import test_bulk_stream
import test_hourly_reports
from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


# What Azure Blob Storage answers when the pre-signed (SAS) download URL handed out by Bing Ads has expired.
EXPIRED_SAS_RESPONSE = HttpResponse(
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly including the signature.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame</AuthenticationErrorDetail></Error>",
    403,
    {"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"},
)


class TestDownloadLinkExpired(BaseTest):
    def _read_and_assert_download_link_error(self, stream_name: str, download_request, config=None) -> None:
        self.http_mocker.get(download_request, EXPIRED_SAS_RESPONSE)
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

        output = read_helper(config or self._config, catalog, expecting_exception=True)

        assert output.records == []
        # The CDK also emits a sync-level summary trace without a stream descriptor; the stream-level trace is the contract here.
        stream_errors = [e.trace.error for e in output.errors if e.trace.error.stream_descriptor]
        assert len(stream_errors) == 1
        error = stream_errors[0]
        assert error.stream_descriptor.name == stream_name
        assert error.failure_type == FailureType.transient_error
        assert error.message == (
            f"The temporary Bing Ads download link for stream '{stream_name}' expired or was rejected "
            "before the file could be downloaded."
        )
        # The link is single-use from the connector's point of view: the same stale URL is not retried.
        self.http_mocker.assert_number_of_calls(download_request, 1)

    @freeze_time("2024-05-06")
    def test_report_download_403_is_a_transient_error_naming_the_stream(self):
        test_hourly_reports.TestAgeGenderAudienceReportHourlyStream.mock_report_apis(self)
        self._read_and_assert_download_link_error("age_gender_audience_report_hourly", RequestBuilder(resource="").build_report_url())

    @freeze_time("2024-05-06")
    def test_custom_report_download_403_is_a_transient_error_naming_the_stream(self):
        config = (
            ConfigBuilder()
            .with_reports_start_date("2024-01-01")
            .with_custom_reports(
                [
                    {
                        "name": "MyCustomReport",
                        "reporting_object": "AgeGenderAudienceReportRequest",
                        "report_columns": ["AccountId", "TimePeriod", "Impressions"],
                        "report_aggregation": "Daily",
                    }
                ]
            )
            .build()
        )
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_generate_report_api(
            endpoint="Submit",
            response_template="generate_report",
            # Serialized exactly as the connector sends it; a Mapping body would make HttpMocker JSON-parse the form-encoded OAuth request.
            body=json.dumps(
                {
                    "ReportRequest": {
                        "ExcludeColumnHeaders": False,
                        "ExcludeReportFooter": True,
                        "ExcludeReportHeader": True,
                        "Format": "Csv",
                        "FormatVersion": "2.0",
                        "ReportName": "AgeGenderAudienceReport",
                        "ReturnOnlyCompleteData": False,
                        "Type": "AgeGenderAudienceReportRequest",
                        "Aggregation": "Daily",
                        "Columns": ["AccountId", "TimePeriod", "Impressions"],
                        "Scope": {"AccountIds": [180535609]},
                        "Time": {
                            "CustomDateRangeStart": {"Day": 1, "Month": 1, "Year": 2024},
                            "CustomDateRangeEnd": {"Day": 6, "Month": 5, "Year": 2024},
                            "ReportTimeZone": "GreenwichMeanTimeDublinEdinburghLisbonLondon",
                        },
                    }
                }
            ).encode(),
        )
        self.mock_generate_report_api(
            endpoint="Poll", response_template="generate_report_poll", body=b'{"ReportRequestId": "thisisthereport_requestid"}'
        )
        # The stream is named after the snake_cased custom report name.
        self._read_and_assert_download_link_error("my_custom_report", RequestBuilder(resource="").build_report_url(), config)

    def test_bulk_download_403_is_a_transient_error_naming_the_stream(self):
        self.download_entity = "AppInstallAds"
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        test_bulk_stream.TestBulkStream.mock_bulk_download_request(self)
        test_bulk_stream.TestBulkStream.mock_bulk_download_status_query(self)
        self._read_and_assert_download_link_error(
            "app_install_ads", RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        )
