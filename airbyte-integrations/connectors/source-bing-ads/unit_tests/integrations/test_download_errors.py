# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/test/download"
EXPIRED_SIGNATURE = "Signature not valid in the specified time frame"
PERMISSION_MESSAGE = "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource."


@pytest.fixture
def download_read(config, requests_mock, mock_auth_token, mock_user_query):
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-05-06T00:00:00"}]},
    )
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
        json={"DownloadRequestId": "bulk-request"},
    )
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
        json={"RequestStatus": "Completed", "ResultFileUrl": DOWNLOAD_URL},
    )
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
        json={"ReportRequestId": "report-request"},
    )
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
        json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": DOWNLOAD_URL}},
    )
    config["reports_start_date"] = "2024-05-05"

    def run(stream_name: str, body: str, headers: dict[str, str]):
        download = requests_mock.get(DOWNLOAD_URL, status_code=403, text=body, headers=headers)
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog, expecting_exception=True)
        assert output.records == []
        assert download.call_count == 1
        return [message.trace.error for message in output.errors if message.trace.error.stream_descriptor]

    return run


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", ["app_install_ads", "ad_performance_report_daily"])
@pytest.mark.parametrize("headers", [{"x-ms-error-code": "AuthenticationFailed"}, {}], ids=["azure-header", "xml-only"])
def test_expired_download_is_transient(download_read, stream_name: str, headers: dict[str, str]) -> None:
    errors = download_read(
        stream_name,
        f"<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>{EXPIRED_SIGNATURE}.</AuthenticationErrorDetail></Error>",
        headers,
    )
    assert [(error.failure_type, error.message) for error in errors] == [
        (FailureType.transient_error, "Bing Ads file download URL is expired.")
    ]
    assert errors[0].stream_descriptor.name == stream_name


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", ["app_install_ads", "ad_performance_report_daily"])
@pytest.mark.parametrize(
    "body, headers",
    [
        ("<Error><Code>AuthorizationPermissionMismatch</Code></Error>", {}),
        (
            "<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>Signature did not match.</AuthenticationErrorDetail></Error>",
            {"x-ms-error-code": "AuthenticationFailed"},
        ),
    ],
    ids=["permission-denied", "non-expired-signature"],
)
def test_other_download_403_keeps_permission_error(download_read, stream_name: str, body: str, headers: dict[str, str]) -> None:
    errors = download_read(stream_name, body, headers)
    assert [(error.failure_type, error.message) for error in errors] == [(FailureType.config_error, PERMISSION_MESSAGE)]
