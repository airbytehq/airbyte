# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/bulkdownloadresultfiles/download.gz"

# What Azure Blob Storage returns for a pre-signed (SAS) URL that is used outside of its validity window.
EXPIRED_URL_ERROR_CODE = "AuthenticationFailed"
EXPIRED_URL_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly including the signature.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Mon, 09 Nov 2026 19:41:55 GMT] - "
    "Expiry [Mon, 09 Nov 2026 20:06:55 GMT] - Current [Mon, 09 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
OTHER_REJECTION_ERROR_CODE = "AuthorizationFailure"
OTHER_REJECTION_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationFailure</Code>'
    "<Message>This request is not authorized to perform this operation.</Message></Error>"
)


@pytest.fixture
def completed_download_jobs(requests_mock: Mocker, mock_auth_token: None, mock_user_query: None) -> None:
    """Bulk and report jobs that complete and hand out DOWNLOAD_URL as the result file."""
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


def _read(stream_name: str, config: dict[str, str | int]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config, None), config, catalog, None, expecting_exception=True)


@freeze_time("2024-05-08")
@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("keywords", id="bulk_stream"),
        pytest.param("account_performance_report_daily", id="report_stream"),
    ],
)
@pytest.mark.parametrize(
    "error_code, body, expected_message",
    [
        pytest.param(EXPIRED_URL_ERROR_CODE, EXPIRED_URL_BODY, "Bing Ads file download URL is expired.", id="expired_url"),
        pytest.param(
            OTHER_REJECTION_ERROR_CODE,
            OTHER_REJECTION_BODY,
            "Bing Ads file download URL is rejected by Azure Blob Storage.",
            id="other_rejection",
        ),
    ],
)
def test_forbidden_file_download_fails_as_transient_error_without_resending_the_url(
    requests_mock: Mocker,
    completed_download_jobs: None,
    config: dict[str, str | int],
    stream_name: str,
    error_code: str,
    body: str,
    expected_message: str,
) -> None:
    config["reports_start_date"] = "2024-05-05"
    requests_mock.get(DOWNLOAD_URL, status_code=403, headers={"x-ms-error-code": error_code, "Content-Type": "application/xml"}, text=body)

    output = _read(stream_name, config)

    assert output.records == []
    # The CDK also emits a sync-level summary error without a stream descriptor; the stream error is the classified one.
    stream_errors = [error.trace.error for error in output.errors if error.trace.error.stream_descriptor]
    assert len(stream_errors) == 1
    assert stream_errors[0].stream_descriptor.name == stream_name
    assert stream_errors[0].failure_type == FailureType.transient_error
    assert stream_errors[0].message == expected_message
    # Resending the request cannot succeed because the rejected URL is part of it, so it is sent once.
    assert [request.url for request in requests_mock.request_history].count(DOWNLOAD_URL) == 1
