#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


EXPIRED_RESPONSE = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. "
    "Signature not valid in the specified time frame: Start [2026-11-12T00:00:00Z] "
    "- Expiry [2026-11-12T00:10:00Z] - Current [2026-11-12T00:20:00Z]</Message></Error>"
)


@freeze_time("2024-01-01")
@pytest.mark.parametrize("stream_name", ["app_install_ads", "ad_performance_report_daily"])
@pytest.mark.parametrize("expired", [True, False], ids=["expired_sas", "permission_denied"])
def test_download_error_trace(stream_name, expired, config, mock_auth_token, mock_user_query, mock_account_query, requests_mock):
    download_url = "https://bingadsappsstorageprod.blob.core.windows.net/download-url"
    if stream_name == "app_install_ads":
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
    requests_mock.get(
        download_url,
        status_code=403,
        headers={"x-ms-error-code": "AuthenticationFailed"} if expired else {},
        text=EXPIRED_RESPONSE if expired else "Forbidden",
    )
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog, expecting_exception=True)

    errors = [message.trace.error for message in output.errors if message.trace.error.stream_descriptor]
    assert errors
    error = errors[0]
    assert error.failure_type == (FailureType.transient_error if expired else FailureType.config_error)
    assert error.message == (
        "Bing Ads file download URL is expired." if expired else "Forbidden. You don't have permission to access this resource."
    )
    assert (EXPIRED_RESPONSE if expired else "Forbidden") in error.internal_message
