# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time
from unit_tests.conftest import create_zip_from_csv, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


pytest_plugins = ["unit_tests.conftest"]


EXPIRED_URL = "https://files.blob.core.windows.net/download?sig=expired"
FRESH_URL = "https://files.blob.core.windows.net/download?sig=fresh"
EXPIRY_XML = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame.</AuthenticationErrorDetail></Error>"
)
BULK_POLL = "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query"
REPORT_POLL = "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll"


def mock_download_job(requests_mock, stream_name, config, poll_urls=None):
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-05-05T00:00:00"}]},
    )
    config["reports_start_date"] = "2024-05-05"
    poll_urls = poll_urls or [EXPIRED_URL]
    if stream_name == "app_install_ads":
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
            json={"DownloadRequestId": "job-1"},
        )
        poll = requests_mock.post(BULK_POLL, [{"json": {"RequestStatus": "Completed", "ResultFileUrl": url}} for url in poll_urls])
    else:
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
            json={"ReportRequestId": "job-1"},
        )
        poll = requests_mock.post(
            REPORT_POLL, [{"json": {"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": url}}} for url in poll_urls]
        )
    return poll


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", ["app_install_ads", "account_performance_report_daily"])
@pytest.mark.parametrize(
    "body, expired",
    [
        pytest.param(EXPIRY_XML, True, id="expired-sas"),
        pytest.param("<Error><Code>AuthorizationPermissionMismatch</Code></Error>", False, id="permission-denied"),
        pytest.param(
            "<Error><Code>AuthenticationFailed</Code><Message>Signature did not match.</Message></Error>",
            False,
            id="invalid-signature",
        ),
    ],
)
def test_download_failure_classification(stream_name, body, expired, requests_mock, config, mock_auth_token, mock_user_query):
    poll = mock_download_job(requests_mock, stream_name, config)
    download = requests_mock.get(EXPIRED_URL, status_code=403, text=body, headers={"Content-Type": "application/xml"})
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog, expecting_exception=True)

    error = next(
        message.trace.error
        for message in output.errors
        if message.trace.error.stream_descriptor and message.trace.error.stream_descriptor.name == stream_name
    )
    assert error.failure_type == (FailureType.transient_error if expired else FailureType.config_error)
    assert error.message == (
        f"The Bing Ads download link for stream '{stream_name}' is expired."
        if expired
        else "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource."
    )
    assert body in error.internal_message
    assert download.call_count == (3 if expired else 1)
    assert poll.call_count == (4 if expired else 2)
    assert not output.records


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", ["app_install_ads", "account_performance_report_daily"])
@pytest.mark.parametrize("expires_during_download", [False, True])
def test_download_uses_refreshed_url(stream_name, expires_during_download, requests_mock, config, mock_auth_token, mock_user_query):
    poll_urls = [EXPIRED_URL, EXPIRED_URL, FRESH_URL] if expires_during_download else [EXPIRED_URL, FRESH_URL]
    poll = mock_download_job(requests_mock, stream_name, config, poll_urls)
    expired_download = requests_mock.get(EXPIRED_URL, status_code=403, text=EXPIRY_XML)
    if stream_name == "app_install_ads":
        content = ("Type,Id,Modified Time\n" "App Install Ad,42,05/05/2024 18:00:14.970\n").encode()
        record_key = "Id"
        expected_value = 42
    else:
        content = create_zip_from_csv("report_base_data")
        record_key = "AccountId"
        expected_value = 1
    fresh_download = requests_mock.get(FRESH_URL, content=content)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog)

    assert not output.errors
    assert [record.record.data[record_key] for record in output.records] == [expected_value]
    assert expired_download.call_count == int(expires_during_download)
    assert fresh_download.call_count == 1
    assert poll.call_count == len(poll_urls)
    for request in poll.request_history[1:]:
        assert request.json() == {"RequestId" if stream_name == "app_install_ads" else "ReportRequestId": "job-1"}
        assert request.headers["CustomerAccountId"] == "1"
        assert request.headers["CustomerId"] == "2"
        assert request.headers["DeveloperToken"] == config["developer_token"]
        assert request.headers["Authorization"] == "Bearer test"
