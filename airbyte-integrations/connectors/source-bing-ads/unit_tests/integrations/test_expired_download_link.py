# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any

import pytest
from conftest import get_source
from requests_mock import Mocker

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/download.csv"
# Body Azure Blob Storage returns for a pre-signed (SAS) URL whose validity window has passed.
EXPIRED_SAS_RESPONSE = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\nTime:2026-11-10T00:00:00.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Tue, 10 Nov 2026 00:00:00 GMT] - "
    "Expiry [Tue, 10 Nov 2026 00:10:00 GMT] - Current [Tue, 10 Nov 2026 00:11:00 GMT]</AuthenticationErrorDetail></Error>"
)


@pytest.fixture
def account(requests_mock: Mocker, mock_auth_token: None, mock_user_query: None) -> None:
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
    )


@pytest.fixture
def completed_jobs(requests_mock: Mocker) -> None:
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


@pytest.mark.parametrize(
    "stream_name, custom_reports",
    [
        pytest.param("budget", [], id="bulk_stream"),
        pytest.param("account_performance_report_daily", [], id="report_stream"),
        pytest.param(
            "my_custom_report",
            [
                {
                    "name": "MyCustomReport",
                    "reporting_object": "AccountPerformanceReportRequest",
                    "report_columns": ["AccountId", "TimePeriod", "Clicks"],
                    "report_aggregation": "Daily",
                }
            ],
            id="custom_report_stream",
        ),
    ],
)
def test_expired_download_link_fails_as_transient_error_naming_the_stream(
    requests_mock: Mocker,
    account: None,
    completed_jobs: None,
    config: dict[str, Any],
    stream_name: str,
    custom_reports: list[dict[str, Any]],
) -> None:
    config["custom_reports"] = custom_reports
    requests_mock.get(DOWNLOAD_URL, status_code=403, text=EXPIRED_SAS_RESPONSE)

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config, None), config, catalog, None, expecting_exception=True)

    # The CDK also emits a sync-level summary error after any stream failure; the stream-level error is the one users see.
    stream_errors = [error.trace.error for error in output.errors if error.trace.error.stream_descriptor]
    assert [(error.stream_descriptor.name, error.failure_type, error.message) for error in stream_errors] == [
        (
            stream_name,
            FailureType.transient_error,
            f"Bing Ads file download for stream '{stream_name}' was rejected because the temporary download link is no longer valid.",
        )
    ]
    assert output.records == []
    # The expired link cannot be revived by asking for the same URL again, so the download is attempted exactly once.
    assert len([request for request in requests_mock.request_history if request.url == DOWNLOAD_URL]) == 1
