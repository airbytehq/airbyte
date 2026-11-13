# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from requests_mock import Mocker

from airbyte_cdk.models import AirbyteErrorTraceMessage, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/bulkdownloadresultfiles/download.gz"

EXPIRED_SIGNATURE_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\nTime:2026-11-10T20:23:43.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Tue, 10 Nov 2026 19:41:55 GMT] - "
    "Expiry [Tue, 10 Nov 2026 20:06:55 GMT] - Current [Tue, 10 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
MISMATCHED_SIGNATURE_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.</Message>"
    "<AuthenticationErrorDetail>Signature did not match. String to sign used was r</AuthenticationErrorDetail></Error>"
)

EXPIRED_URL_MESSAGE = "Bing Ads file download URL is expired."
DEFAULT_FORBIDDEN_MESSAGE = "Forbidden. You don't have permission to access this resource."


def _mock_bulk_job(requests_mock: Mocker) -> None:
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
        json={"DownloadRequestId": "download-id"},
    )
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
        json={"RequestStatus": "Completed", "ResultFileUrl": DOWNLOAD_URL, "PercentComplete": 100},
    )


def _mock_report_job(requests_mock: Mocker) -> None:
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
        json={"ReportRequestId": "report-id"},
    )
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
        json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": DOWNLOAD_URL}},
    )


def _read_with_forbidden_download(
    requests_mock: Mocker, config: dict[str, str | int], stream_name: str, response_body: str
) -> tuple[EntrypointOutput, int]:
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
    )
    _mock_bulk_job(requests_mock)
    _mock_report_job(requests_mock)
    requests_mock.get(DOWNLOAD_URL, status_code=403, headers={"x-ms-error-code": "AuthenticationFailed"}, text=response_body)

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog, expecting_exception=True)
    download_attempts = len([request for request in requests_mock.request_history if request.url == DOWNLOAD_URL])
    return output, download_attempts


def _stream_error(output: EntrypointOutput, stream_name: str) -> AirbyteErrorTraceMessage:
    stream_errors = [
        message.trace.error
        for message in output.errors
        if message.trace.error.stream_descriptor and message.trace.error.stream_descriptor.name == stream_name
    ]
    assert len(stream_errors) == 1
    return stream_errors[0]


@pytest.mark.parametrize("stream_name", ["keywords", "account_performance_report_daily"], ids=["bulk_stream", "report_stream"])
def test_expired_download_url_fails_as_transient_error(
    requests_mock: Mocker, mock_auth_token: None, mock_user_query: None, config: dict[str, str | int], stream_name: str
) -> None:
    output, download_attempts = _read_with_forbidden_download(requests_mock, config, stream_name, EXPIRED_SIGNATURE_BODY)

    assert output.records == []
    error = _stream_error(output, stream_name)
    assert error.failure_type == FailureType.transient_error
    assert error.message == EXPIRED_URL_MESSAGE
    assert "Signature not valid in the specified time frame" in error.internal_message
    assert download_attempts == 1


@pytest.mark.parametrize("stream_name", ["keywords", "account_performance_report_daily"], ids=["bulk_stream", "report_stream"])
def test_other_forbidden_download_keeps_default_classification(
    requests_mock: Mocker, mock_auth_token: None, mock_user_query: None, config: dict[str, str | int], stream_name: str
) -> None:
    output, download_attempts = _read_with_forbidden_download(requests_mock, config, stream_name, MISMATCHED_SIGNATURE_BODY)

    assert output.records == []
    error = _stream_error(output, stream_name)
    assert error.failure_type == FailureType.config_error
    assert error.message.endswith(DEFAULT_FORBIDDEN_MESSAGE)
    assert download_attempts == 1
