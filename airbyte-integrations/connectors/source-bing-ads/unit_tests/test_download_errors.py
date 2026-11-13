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
            {"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"},
            "<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>"
            "Signature not valid in the specified time frame</AuthenticationErrorDetail></Error>",
            "transient_error",
            "Bing Ads file download URL is expired.",
        ),
        (
            {},
            "Forbidden",
            "config_error",
            "Forbidden. You don't have permission to access this resource.",
        ),
    ],
    ids=["expired_signature", "plain_forbidden"],
)
def test_download_error_classification(
    stream_name, headers, body, failure_type, message, config, mock_auth_token, mock_user_query, mock_account_query, requests_mock
):
    download_url = "https://bingadsappsstorageprod.blob.core.windows.net/download-url"
    if stream_name == "keywords":
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
            json={"DownloadRequestId": "bulk-request"},
        )
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
            json={"RequestStatus": "Completed", "ResultFileUrl": download_url},
        )
    else:
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
            json={"ReportRequestId": "report-request"},
        )
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
            json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": download_url}},
        )
    download = requests_mock.get(download_url, status_code=403, headers=headers, text=body)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    output = read(get_source(config), config, catalog)

    assert download.called
    errors = [
        error.trace.error
        for error in output.errors
        if error.trace.error.stream_descriptor and error.trace.error.stream_descriptor.name == stream_name
    ]
    assert errors
    actual_message = errors[0].message
    if failure_type == "config_error":
        actual_message = actual_message.removeprefix("HTTP Status Code: 403. Error: ")
    assert (actual_message, errors[0].failure_type.value) == (message, failure_type)
