# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import AirbyteErrorTraceMessage, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/bulkdownloadresultfiles/download.gz"

# Body Azure Blob Storage returns for a pre-signed (SAS) download URL that is past its expiry time.
EXPIRED_SIGNATURE_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly including the signature.\n"
    "RequestId:00000000-0000-0000-0000-000000000000\nTime:2026-11-10T20:23:43.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Tue, 10 Nov 2026 19:41:55 GMT] - "
    "Expiry [Tue, 10 Nov 2026 20:06:55 GMT] - Current [Tue, 10 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
# Body Azure Blob Storage returns for a 403 that is not an expiry (the signature itself is wrong).
MISMATCHED_SIGNATURE_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly including the signature.</Message>"
    "<AuthenticationErrorDetail>Signature did not match. String to sign used was r</AuthenticationErrorDetail></Error>"
)

STREAMS = [
    pytest.param("keywords", id="bulk"),
    pytest.param("budget_summary_report", id="report"),
]


def _read_with_failing_download(requests_mock: Mocker, config: dict[str, str | int], stream_name: str, body: str) -> EntrypointOutput:
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
    )
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds", json={"DownloadRequestId": "download-id"}
    )
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
        json={"RequestStatus": "Completed", "ResultFileUrl": DOWNLOAD_URL, "PercentComplete": 100},
    )
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit", json={"ReportRequestId": "report-id"}
    )
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
        json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": DOWNLOAD_URL}},
    )
    requests_mock.get(
        DOWNLOAD_URL,
        status_code=403,
        text=body,
        headers={"Content-Type": "application/xml", "x-ms-error-code": "AuthenticationFailed"},
    )
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog, expecting_exception=True)


def _stream_error(output: EntrypointOutput, stream_name: str) -> AirbyteErrorTraceMessage:
    # The read also emits a final sync-level trace without a stream descriptor; the stream-level trace carries the classification.
    stream_errors = [
        message.trace.error
        for message in output.errors
        if message.trace.error.stream_descriptor and message.trace.error.stream_descriptor.name == stream_name
    ]
    assert len(stream_errors) == 1
    return stream_errors[0]


def _download_request_count(requests_mock: Mocker) -> int:
    return len([request for request in requests_mock.request_history if request.method == "GET" and request.url == DOWNLOAD_URL])


@freeze_time("2024-02-26")
@pytest.mark.parametrize("stream_name", STREAMS)
def test_expired_download_url_fails_as_transient_error_without_retry(
    requests_mock: Mocker, mock_auth_token: None, mock_user_query: None, config: dict[str, str | int], stream_name: str
) -> None:
    output = _read_with_failing_download(requests_mock, config, stream_name, EXPIRED_SIGNATURE_BODY)

    assert output.records == []
    error = _stream_error(output, stream_name)
    assert error.failure_type == FailureType.transient_error
    assert error.message == "Bing Ads file download URL is expired."
    # The expired URL is not requested again: only a new poll returns a usable URL.
    assert _download_request_count(requests_mock) == 1


@freeze_time("2024-02-26")
@pytest.mark.parametrize("stream_name", STREAMS)
def test_other_download_403_keeps_permission_config_error(
    requests_mock: Mocker, mock_auth_token: None, mock_user_query: None, config: dict[str, str | int], stream_name: str
) -> None:
    output = _read_with_failing_download(requests_mock, config, stream_name, MISMATCHED_SIGNATURE_BODY)

    assert output.records == []
    error = _stream_error(output, stream_name)
    assert error.failure_type == FailureType.config_error
    # The CDK default 403 message gained an "HTTP Status Code: 403. Error: " prefix in CDK 7, so only the stable suffix is asserted.
    assert error.message.endswith("Forbidden. You don't have permission to access this resource.")
    assert _download_request_count(requests_mock) == 1
