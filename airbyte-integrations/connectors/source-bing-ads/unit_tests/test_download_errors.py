#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


@freeze_time("2025-01-01")
@pytest.mark.parametrize("stream_name", ["keywords", "ad_performance_report_daily"])
@pytest.mark.parametrize("expired", [True, False], ids=["expired_signature", "other_forbidden"])
def test_download_error_classification(
    stream_name, expired, config, mock_auth_token, mock_user_query, mock_account_query, requests_mock
):
    config["reports_start_date"] = "2024-12-31"
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "LastModifiedTime": "2022-02-02T22:22:22"}]},
    )
    download_url = "https://bingadsappsstorageprod.blob.core.windows.net/download-url"
    is_report = stream_name == "ad_performance_report_daily"
    if is_report:
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
            json={"ReportRequestId": "report-id"},
        )
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
            json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": download_url}},
        )
    else:
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
            json={"DownloadRequestId": "bulk-id"},
        )
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
            json={"RequestStatus": "Completed", "ResultFileUrl": download_url},
        )

    code = "AuthenticationFailed" if expired else "AuthorizationPermissionMismatch"
    message = (
        "Signature not valid in the specified time frame: Start [...] - Expiry [...] - Current [...]"
        if expired
        else "Permission denied."
    )
    download = requests_mock.get(
        download_url,
        status_code=403,
        headers={"x-ms-error-code": code, "Content-Type": "application/xml"},
        text=f"<Error><Code>{code}</Code><Message>{message}</Message></Error>",
    )
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog, expecting_exception=True)

    assert download.called
    errors = [message.trace.error for message in output.errors if message.trace.error.stream_descriptor]
    assert errors
    for error in errors:
        assert error.failure_type.value == ("transient_error" if expired else "config_error")
        if expired:
            assert "Bing Ads file download URL is expired." in error.message
        else:
            assert error.message == "Forbidden. You don't have permission to access this resource."
