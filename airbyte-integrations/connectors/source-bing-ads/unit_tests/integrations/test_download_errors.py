# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/download.csv"


@freeze_time("2024-05-08")
@pytest.mark.parametrize("stream_name", ["labels", "account_performance_report_daily"])
def test_download_error(
    requests_mock: Mocker,
    mock_auth_token: None,
    mock_user_query: None,
    config: dict,
    stream_name: str,
) -> None:
    config["reports_start_date"] = "2024-05-07"
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
    )
    if stream_name == "labels":
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
            json={"DownloadRequestId": "download-id"},
        )
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
            json={"RequestStatus": "Completed", "ResultFileUrl": DOWNLOAD_URL, "PercentComplete": 100},
        )
    else:
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
            json={"ReportRequestId": "report-id"},
        )
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
            json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": DOWNLOAD_URL}},
        )
    requests_mock.get(
        DOWNLOAD_URL,
        status_code=403,
        headers={"Content-Type": "application/xml"},
        text=(
            '<?xml version="1.0" encoding="utf-8"?><Error>'
            "<Code>AuthenticationFailed</Code>"
            "<Message>Server failed to authenticate the request. Make sure the value of Authorization header "
            "is formed correctly including the signature.\nRequestId:test-request\nTime:2024-05-08T00:00:00Z</Message>"
            "<AuthenticationErrorDetail>Signature not valid in the specified time frame</AuthenticationErrorDetail></Error>"
        ),
    )
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    output = read(get_source(config), config, catalog, expecting_exception=True)

    assert not output.records
    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type.value == "transient_error"
    assert error.message == (
        f"The Bing Ads download link for stream '{stream_name}' expired or is no longer valid before the file could be downloaded. "
        "The sync will retry."
    )
