# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json

import test_hourly_reports
from base_test import BaseTest
from config_builder import ConfigBuilder
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


_AZURE_SAS_EXPIRED_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed "
    "correctly including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\nTime:2024-05-06T00:20:00.0000000Z"
    "</Message><AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [Mon, 06 May 2024 00:00:00 GMT] - Expiry [Mon, 06 May 2024 00:10:00 GMT] - Current [Mon, 06 May 2024 00:20:00 GMT]"
    "</AuthenticationErrorDetail></Error>"
)


def _azure_sas_expired_response() -> HttpResponse:
    return HttpResponse(
        _AZURE_SAS_EXPIRED_BODY,
        403,
        {"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"},
    )


_EXPECTED_MESSAGE = "The Bing Ads file download URL expired before the file could be downloaded. The sync will retry."


class TestDownloadUrlExpired(BaseTest):
    def _mock_accounts(self) -> None:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )

    def _read(self, stream_name: str, config: dict):
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        return read_helper(config, catalog, expecting_exception=True)

    def _assert_transient_expired_url_error(self, output, stream_name: str) -> None:
        assert not output.records
        stream_errors = [
            message.trace.error
            for message in output.errors
            if message.trace.error.stream_descriptor and message.trace.error.stream_descriptor.name == stream_name
        ]
        assert len(stream_errors) == 1
        assert stream_errors[0].failure_type == FailureType.transient_error
        assert stream_errors[0].message == _EXPECTED_MESSAGE

    def test_bulk_stream_expired_download_url_is_transient_error(self) -> None:
        self._mock_accounts()
        self.http_mocker.post(
            RequestBuilder(resource="Bulk/v13/Campaigns/DownloadByAccountIds", api="bulk")
            .with_body(
                '{"AccountIds": ["180535609"], "DataScope": "EntityData", "DownloadEntities": ["Budgets"], '
                '"DownloadFileType": "Csv", "FormatVersion": "6.0", "CompressionType": "GZip"}'
            )
            .build(),
            HttpResponse(json.dumps(find_template(resource="bulk_download", execution_folder=__file__)), 200),
        )
        self.http_mocker.post(
            RequestBuilder(resource="Bulk/v13/BulkDownloadStatus/Query", api="bulk").with_body('{"RequestId": "TestDownloadRequestId"}').build(),
            HttpResponse(json.dumps(find_template(resource="bulk_status", execution_folder=__file__)), 200),
        )
        download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        self.http_mocker.get(download_request, _azure_sas_expired_response())

        output = self._read("budget", self._config)

        self._assert_transient_expired_url_error(output, "budget")
        self.http_mocker.assert_number_of_calls(download_request, 1)

    @freeze_time("2024-05-06")
    def test_report_stream_expired_download_url_is_transient_error(self) -> None:
        stream_name = "age_gender_audience_report_hourly"
        test_hourly_reports.TestAgeGenderAudienceReportHourlyStream.mock_report_apis(self)
        download_request = RequestBuilder(resource="").build_report_url()
        self.http_mocker.get(download_request, _azure_sas_expired_response())

        output = self._read(stream_name, ConfigBuilder().with_reports_start_date("2024-01-01").build())

        self._assert_transient_expired_url_error(output, stream_name)
        self.http_mocker.assert_number_of_calls(download_request, 1)
