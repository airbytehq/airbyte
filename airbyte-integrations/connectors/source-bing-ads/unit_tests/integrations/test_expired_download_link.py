# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/download.csv"
BULK_API_URL = "https://bulk.api.bingads.microsoft.com/Bulk/v13"
REPORTING_API_URL = "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport"

# Body Azure Blob Storage returns when the pre-signed (SAS) download URL handed out by Bing Ads has expired.
EXPIRED_SAS_RESPONSE_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:5c1f3a2e-801e-0041-2b6f-1f6a4d000000\nTime:2026-11-12T09:41:07.1234567Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Thu, 12 Nov 2026 09:20:55 GMT] - "
    "Expiry [Thu, 12 Nov 2026 09:35:55 GMT] - Current [Thu, 12 Nov 2026 09:41:07 GMT]</AuthenticationErrorDetail></Error>"
)


def _mock_completed_job(requests_mock: Mocker, api: str) -> None:
    if api == "bulk":
        requests_mock.post(f"{BULK_API_URL}/Campaigns/DownloadByAccountIds", json={"DownloadRequestId": "download-id"})
        requests_mock.post(
            f"{BULK_API_URL}/BulkDownloadStatus/Query",
            json={"RequestStatus": "Completed", "ResultFileUrl": DOWNLOAD_URL, "PercentComplete": 100},
        )
    else:
        requests_mock.post(f"{REPORTING_API_URL}/Submit", json={"ReportRequestId": "report-id"})
        requests_mock.post(
            f"{REPORTING_API_URL}/Poll",
            json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": DOWNLOAD_URL}},
        )


@freeze_time("2024-05-08")
@pytest.mark.parametrize(
    "stream_name, api",
    [
        pytest.param("budget", "bulk", id="bulk_stream"),
        pytest.param("account_performance_report_daily", "reporting", id="report_stream"),
        pytest.param("custom_report", "reporting", id="custom_report_stream"),
    ],
)
def test_expired_download_link_fails_stream_as_transient_error(
    requests_mock: Mocker,
    mock_auth_token: None,
    mock_user_query: None,
    config: dict[str, object],
    stream_name: str,
    api: str,
) -> None:
    config["custom_reports"] = [
        {
            "name": "custom_report",
            "reporting_object": "AccountPerformanceReportRequest",
            "report_columns": ["AccountId", "TimePeriod", "Clicks"],
            "report_aggregation": "Daily",
        }
    ]
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
    )
    _mock_completed_job(requests_mock, api)
    requests_mock.get(DOWNLOAD_URL, status_code=403, text=EXPIRED_SAS_RESPONSE_BODY)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    output = read(get_source(config, None), config, catalog, expecting_exception=True)

    assert output.records == []
    error = next(message.trace.error for message in output.errors if message.trace.error.stream_descriptor)
    assert error.stream_descriptor.name == stream_name
    assert error.failure_type == FailureType.transient_error
    assert error.message == (
        "Download link issued by Bing Ads for the report or bulk file is expired or no longer valid. The file was not downloaded."
    )
    # An expired link never becomes valid again, so the connector must not keep requesting it.
    assert [request.method for request in requests_mock.request_history if request.url == DOWNLOAD_URL] == ["GET"]
