# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""
Bing Ads returns pre-signed Azure Blob Storage URLs for bulk and report files. When such a URL expires before the
file is downloaded, Azure answers ``403 AuthenticationFailed`` with ``Signature not valid in the specified time frame``
in its XML body. The download request carries no user credentials, so no 403 on it can be fixed by changing the
connector configuration. These tests pin that the connector reports such a 403 as a transient "download URL expired"
error instead of the CDK's generic "You don't have permission" config error, and fails without retrying the same URL.
"""

import pytest
from conftest import get_source
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/bulkdownloadresultfiles/download.gz?se=expired&sig=sig"

EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed "
    "correctly including the signature.</Message><AuthenticationErrorDetail>Signature not valid in the specified "
    "time frame: Start [Wed, 01 Jan 2025 19:41:55 GMT] - Expiry [Wed, 01 Jan 2025 20:06:55 GMT] - "
    "Current [Wed, 01 Jan 2025 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
)
PERMISSION_MISMATCH_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationPermissionMismatch</Code>'
    "<Message>This request is not authorized to perform this operation using this permission.</Message></Error>"
)
EXPIRED_MESSAGE = "Bing Ads file download URL is expired or no longer valid."


@pytest.fixture
def account(requests_mock: Mocker, mock_auth_token: None, mock_user_query: None) -> None:
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
    )


def _mock_bulk_job(requests_mock: Mocker) -> None:
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds", json={"DownloadRequestId": "download-id"}
    )
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
        json={"RequestStatus": "Completed", "ResultFileUrl": DOWNLOAD_URL, "PercentComplete": 100},
    )


def _mock_report_job(requests_mock: Mocker) -> None:
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit", json={"ReportRequestId": "report-id"}
    )
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
        json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": DOWNLOAD_URL}},
    )


@freeze_time("2024-05-08")
@pytest.mark.parametrize(
    "stream_name, mock_job",
    [
        pytest.param("app_install_ads", _mock_bulk_job, id="bulk"),
        pytest.param("account_performance_report_daily", _mock_report_job, id="report"),
    ],
)
@pytest.mark.parametrize(
    "error_code, body",
    [
        pytest.param("AuthenticationFailed", EXPIRED_SAS_BODY, id="expired_sas_url"),
        pytest.param("AuthorizationPermissionMismatch", PERMISSION_MISMATCH_BODY, id="sas_permission_mismatch"),
    ],
)
def test_forbidden_file_download_fails_as_transient_expired_url(
    requests_mock: Mocker,
    account: None,
    config: dict[str, str | int],
    stream_name: str,
    mock_job,
    error_code: str,
    body: str,
) -> None:
    mock_job(requests_mock)
    requests_mock.get(
        DOWNLOAD_URL, status_code=403, text=body, headers={"Content-Type": "application/xml", "x-ms-error-code": error_code}
    )

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config, {}), config, catalog, None, expecting_exception=True)

    # The CDK also emits a combined "streams did not sync successfully" summary that is always a config_error by design;
    # the error users act on is the one attached to the failing stream.
    stream_errors = [
        message.trace.error
        for message in output.errors
        if message.trace.error.stream_descriptor and message.trace.error.stream_descriptor.name == stream_name
    ]
    assert output.records == []
    assert [(error.failure_type, error.message) for error in stream_errors] == [(FailureType.transient_error, EXPIRED_MESSAGE)]
    # The raw Azure error stays available to engineers in the internal message.
    assert error_code in stream_errors[0].internal_message
    # The download fails on the first response instead of being retried against the same URL.
    assert len([request for request in requests_mock.request_history if request.url == DOWNLOAD_URL]) == 1
