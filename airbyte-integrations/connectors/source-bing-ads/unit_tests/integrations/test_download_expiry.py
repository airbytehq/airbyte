# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
from conftest import create_zip_from_csv, get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


EXPIRED_SAS = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame.</AuthenticationErrorDetail></Error>"
)
STALE_URL = "https://example.blob.core.windows.net/download?sig=stale"
FRESH_URL = "https://example.blob.core.windows.net/download?sig=fresh"
STREAMS = ["app_install_ads", "account_performance_report_daily"]


@pytest.fixture
def download_read(config, requests_mock, mock_auth_token, mock_user_query):
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2022-02-02T22:22:22"}]},
    )
    config["reports_start_date"] = "2024-01-01"

    def setup(stream_name, *, recover=False, error=EXPIRED_SAS):
        bulk = stream_name == "app_install_ads"
        creation_url = (
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds"
            if bulk
            else "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit"
        )
        poll_url = (
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query"
            if bulk
            else "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll"
        )
        requests_mock.post(creation_url, json={"DownloadRequestId" if bulk else "ReportRequestId": "request-1"})

        def status(url):
            return (
                {"RequestStatus": "Completed", "ResultFileUrl": url}
                if bulk
                else {"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": url}}
            )

        poll = requests_mock.post(
            poll_url,
            [{"json": status(STALE_URL)}, {"json": status(STALE_URL)}, {"json": status(FRESH_URL if recover else STALE_URL)}],
        )
        stale = requests_mock.get(STALE_URL, status_code=403, text=error, headers={"Content-Type": "application/xml"})
        content = (
            (Path(__file__).parent.parent / "resource/response/app_install_ads.csv").read_bytes()
            if bulk
            else create_zip_from_csv("report_base_data")
        )
        fresh = requests_mock.get(FRESH_URL, content=content)
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog, expecting_exception=not recover)
        return output, poll, stale, fresh

    return setup


@freeze_time("2024-01-02")
@pytest.mark.parametrize("stream_name", STREAMS)
def test_read_refreshes_expired_download_link(download_read, stream_name):
    output, poll, stale, fresh = download_read(stream_name, recover=True)

    assert output.errors == []
    assert len(output.records) == 1
    record = output.records[0].record.data
    if stream_name == "app_install_ads":
        assert record["App Id"] == 111111111
        assert record["Account Id"] == 1
    else:
        assert record["TimePeriod"] == "2023-01-01"
        assert record["AccountId"] == 1
    assert stale.call_count == 1
    assert fresh.call_count == 1
    assert poll.call_count == 3
    for request in poll.request_history:
        assert request.json() == {"RequestId" if stream_name == "app_install_ads" else "ReportRequestId": "request-1"}
        assert request.headers["Authorization"] == "Bearer test"
        assert request.headers["CustomerAccountId"] == "1"
        assert request.headers["CustomerId"] == "2"


@freeze_time("2024-01-02")
@pytest.mark.parametrize("stream_name", STREAMS)
def test_read_reports_persistent_download_expiry_as_transient(download_read, stream_name):
    output, poll, stale, fresh = download_read(stream_name)

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.transient_error
    assert error.message == f"The Bing Ads download link for stream '{stream_name}' is expired."
    assert "AuthenticationFailed" in error.internal_message
    assert "Signature not valid in the specified time frame" in error.internal_message
    assert output.records == []
    assert stale.call_count == 2
    assert fresh.call_count == 0
    assert poll.call_count == 3


@freeze_time("2024-01-02")
@pytest.mark.parametrize("stream_name", STREAMS)
@pytest.mark.parametrize(
    "body",
    [
        "<Error><Code>AuthorizationPermissionMismatch</Code><Message>Permission denied.</Message></Error>",
        "<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>Signature did not match.</AuthenticationErrorDetail></Error>",
    ],
)
def test_read_keeps_non_expiry_403_as_config_error(download_read, stream_name, body):
    output, poll, stale, fresh = download_read(stream_name, error=body)

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert error.message == "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource."
    assert stale.call_count == 1
    assert fresh.call_count == 0
    assert output.records == []
