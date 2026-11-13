# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import test_hourly_reports
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from test_bulk_stream import TestBulkStream
from test_report_stream import TestReportStream

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


# Shape of the response Azure Blob Storage returns once the SAS window of a Bing Ads download URL has passed.
EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\nTime:2026-11-05T20:23:43.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Thu, 05 Nov 2026 19:41:55 GMT] - "
    "Expiry [Thu, 05 Nov 2026 20:06:55 GMT] - Current [Thu, 05 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
EXPIRED_SAS_RESPONSE = HttpResponse(EXPIRED_SAS_BODY, 403, headers={"x-ms-error-code": "AuthenticationFailed"})
# A 403 from the same host that is not caused by an expired SAS window.
OTHER_FORBIDDEN_RESPONSE = HttpResponse(
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationFailure</Code>'
    "<Message>This request is not authorized to perform this operation.</Message></Error>",
    403,
    headers={"x-ms-error-code": "AuthorizationFailure"},
)

EXPIRED_URL_MESSAGE = "Bing Ads file download URL is expired."
# The CDK's own message for an unclassified 403, whose wording differs between CDK versions.
DEFAULT_FORBIDDEN_MESSAGE = DEFAULT_ERROR_MAPPING[403].error_message


class DownloadErrorContract:
    """Reads one stream whose file download fails and checks the error surfaced to the user."""

    def download_request(self) -> HttpRequest:
        raise NotImplementedError

    def mock_everything_but_download(self) -> None:
        raise NotImplementedError

    def _read_with_failing_download(self, response: HttpResponse):
        self.mock_everything_but_download()
        self._download_request = self.download_request()
        self.http_mocker.get(self._download_request, response)
        catalog = CatalogBuilder().with_stream(self.stream_name, SyncMode.full_refresh).build()
        return read_helper(self._config, catalog, None, expecting_exception=True)

    def _assert_single_error(self, output, failure_type: FailureType, message: str):
        assert len(output.records) == 0
        # The last trace is the CDK's "streams did not sync successfully" roll-up; the stream error is the one users act on.
        stream_errors = [
            error.trace.error
            for error in output.errors
            if error.trace.error.stream_descriptor and error.trace.error.stream_descriptor.name == self.stream_name
        ]
        assert [(error.failure_type, error.message) for error in stream_errors] == [(failure_type, message)]
        # The same URL stays expired, so it must not be requested again.
        self.http_mocker.assert_number_of_calls(self._download_request, 1)
        return stream_errors[0]

    @freeze_time("2024-05-06")
    def test_expired_download_url_is_a_transient_error(self):
        output = self._read_with_failing_download(EXPIRED_SAS_RESPONSE)
        error = self._assert_single_error(output, FailureType.transient_error, EXPIRED_URL_MESSAGE)
        # The raw Azure response stays available for debugging.
        assert "Signature not valid in the specified time frame" in error.internal_message

    @freeze_time("2024-05-06")
    def test_other_forbidden_download_keeps_config_error(self):
        output = self._read_with_failing_download(OTHER_FORBIDDEN_RESPONSE)
        self._assert_single_error(output, FailureType.config_error, DEFAULT_FORBIDDEN_MESSAGE)


class TestBulkDownloadUrlExpired(DownloadErrorContract, TestBulkStream):
    stream_name = "budget"
    download_entity = "Budgets"

    def download_request(self) -> HttpRequest:
        return RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()

    def mock_everything_but_download(self) -> None:
        self.mock_user_query_api(response_template="user_query")
        self.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        self.mock_bulk_download_request()
        self.mock_bulk_download_status_query()


class TestReportDownloadUrlExpired(DownloadErrorContract, TestReportStream):
    stream_name = "age_gender_audience_report_hourly"

    def download_request(self) -> HttpRequest:
        return RequestBuilder(resource="").build_report_url()

    def mock_everything_but_download(self) -> None:
        test_hourly_reports.TestAgeGenderAudienceReportHourlyStream.mock_report_apis(self)
