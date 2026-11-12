# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


@freeze_time("2024-01-01")
@pytest.mark.parametrize("stream_name", ["keywords", "ad_performance_report_daily"])
@pytest.mark.parametrize(
    "headers, body, failure_type, message",
    [
        (
            {"x-ms-error-code": "AuthenticationFailed"},
            "<Error><Code>AuthenticationFailed</Code><Message>Signature not valid in the specified time frame: "
            "Start [2024-01-01T00:00:00Z] - Expiry [2024-01-01T00:10:00Z] - Current [2024-01-01T00:11:00Z]"
            "</Message></Error>",
            "transient_error",
            "Bing Ads file download URL is expired.",
        ),
        ({}, "", "config_error", "Forbidden. You don't have permission to access this resource."),
    ],
    ids=["expired-sas", "plain-forbidden"],
)
def test_download_error(
    stream_name, headers, body, failure_type, message, config, mock_auth_token, mock_user_query, mock_account_query, requests_mock
):
    config["reports_start_date"] = "2023-12-31"
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 10, "LastModifiedTime": "2022-02-02T22:22:22"}]},
    )
    download_url = "https://bingadsappsstorageprod.blob.core.windows.net/download-url"
    if stream_name == "keywords":
        create_url = "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds"
        poll_url = "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query"
        creation_response = {"DownloadRequestId": "request-id"}
        polling_response = {"RequestStatus": "Completed", "ResultFileUrl": download_url}
    else:
        create_url = "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit"
        poll_url = "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll"
        creation_response = {"ReportRequestId": "request-id"}
        polling_response = {"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": download_url}}

    requests_mock.post(create_url, json=creation_response)
    requests_mock.post(poll_url, json=polling_response)
    download = requests_mock.get(download_url, status_code=403, headers=headers, text=body)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    output = read(get_source(config), config, catalog, expecting_exception=True)

    errors = [error.trace.error for error in output.errors if error.trace.error.stream_descriptor]
    assert errors
    assert {error.failure_type.value for error in errors} == {failure_type}
    assert {error.message for error in errors} == {message}
    assert download.call_count == 1
