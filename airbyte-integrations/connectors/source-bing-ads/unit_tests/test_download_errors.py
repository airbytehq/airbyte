# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


@freeze_time("2025-01-01")
@pytest.mark.parametrize("stream_name", ["keywords", "keyword_performance_report_daily"])
@pytest.mark.parametrize(
    "headers, body, failure_type, message",
    [
        (
            {"x-ms-error-code": "AuthenticationFailed"},
            "<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>"
            "Signature not valid in the specified time frame: Start [2024-12-31] - "
            "Expiry [2024-12-31] - Current [2025-01-01]</AuthenticationErrorDetail></Error>",
            "transient_error",
            "Bing Ads file download URL is expired.",
        ),
        (
            {},
            "<Error><Code>AuthorizationPermissionMismatch</Code></Error>",
            "config_error",
            "Forbidden. You don't have permission to access this resource.",
        ),
        (
            {"X-Ms-Error-Code": "AuthenticationFailed"},
            "<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>"
            "Signature did not match.</AuthenticationErrorDetail></Error>",
            "config_error",
            "Forbidden. You don't have permission to access this resource.",
        ),
    ],
    ids=["expired-signature", "permission-denied", "invalid-signature"],
)
def test_download_error_classification(
    stream_name, headers, body, failure_type, message, config, requests_mock, mock_auth_token, mock_user_query
):
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2022-02-02T22:22:22"}]},
    )
    download_url = "https://bingadsappsstorageprod.blob.core.windows.net/bulkdownloadresultfiles/file.gz?sig=expired"
    if stream_name == "keywords":
        creation = requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
            json={"DownloadRequestId": "bulk-request"},
        )
        polling = requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
            json={"RequestStatus": "Completed", "ResultFileUrl": download_url},
        )
    else:
        creation = requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
            json={"ReportRequestId": "report-request"},
        )
        polling = requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
            json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": download_url}},
        )
    download = requests_mock.get(download_url, status_code=403, headers=headers, text=body)

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog, expecting_exception=True)

    stream_errors = [entry.trace.error for entry in output.errors if entry.trace.error.stream_descriptor]
    assert len(stream_errors) == 1
    assert stream_errors[0].failure_type.value == failure_type
    assert stream_errors[0].message == message
    assert output.records == []
    assert download.call_count == 1
    assert creation.call_count == 1
    assert polling.call_count == 1
