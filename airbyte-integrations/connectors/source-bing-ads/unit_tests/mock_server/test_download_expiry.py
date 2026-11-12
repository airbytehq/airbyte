# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import gzip

import pytest
from conftest import create_zip_from_csv, get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


EXPIRED_URL = "https://example.blob.core.windows.net/file?sig=expired"
FRESH_URL = "https://example.blob.core.windows.net/file?sig=fresh"
EXPIRY_RESPONSE = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [Thu, 01 Jan 2026 00:00:00 GMT] - Expiry [Thu, 01 Jan 2026 00:10:00 GMT]"
    "</AuthenticationErrorDetail></Error>"
)
REPORT_STREAM = "account_performance_report_daily"
BULK_STREAM = "app_install_ads"


@pytest.fixture(params=[REPORT_STREAM, BULK_STREAM])
def download_flow(request, requests_mock, mock_auth_token, mock_user_query, config):
    stream_name = request.param
    config["reports_start_date"] = "2023-01-01"
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2023-01-01T00:00:00"}]},
    )
    is_bulk = stream_name == BULK_STREAM
    base_url = "https://bulk.api.bingads.microsoft.com/" if is_bulk else "https://reporting.api.bingads.microsoft.com/"
    creation_path = "Bulk/v13/Campaigns/DownloadByAccountIds" if is_bulk else "Reporting/v13/GenerateReport/Submit"
    poll_path = "Bulk/v13/BulkDownloadStatus/Query" if is_bulk else "Reporting/v13/GenerateReport/Poll"
    requests_mock.post(
        base_url + creation_path,
        json={"DownloadRequestId" if is_bulk else "ReportRequestId": "request-1"},
    )
    poll_url = base_url + poll_path

    def poll_response(url):
        if is_bulk:
            return {"RequestStatus": "Completed", "ResultFileUrl": url}
        return {"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": url}}

    payload = (
        gzip.compress(b"Type,Id,Parent Id,Modified Time\nApp Install Ad,42,7,01/01/2023 00:00:00.000\n")
        if is_bulk
        else create_zip_from_csv("report_base_data")
    )
    return stream_name, config, poll_url, poll_response, payload


def read_download(download_flow):
    stream_name, config, _, _, _ = download_flow
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog)


@freeze_time("2023-01-02")
@pytest.mark.parametrize("expires_during_download", [False, True], ids=["refresh_before_download", "refresh_after_expiry"])
def test_download_refreshes_url_and_recovers(download_flow, requests_mock, expires_during_download):
    stream_name, _, poll_url, poll_response, payload = download_flow
    poll = requests_mock.post(
        poll_url,
        [
            {"json": poll_response(EXPIRED_URL)},
            {"json": poll_response(EXPIRED_URL if expires_during_download else FRESH_URL)},
            {"json": poll_response(FRESH_URL)},
        ],
    )
    expired = requests_mock.get(EXPIRED_URL, status_code=403, text=EXPIRY_RESPONSE)
    fresh = requests_mock.get(FRESH_URL, content=payload)

    output = read_download(download_flow)

    assert not output.errors
    assert len(output.records) == 1
    record = output.records[0].record.data
    if stream_name == BULK_STREAM:
        assert record["Id"] == 42
    else:
        assert record["TimePeriod"] == "2023-01-01"
    assert expired.call_count == int(expires_during_download)
    assert fresh.call_count == 1
    assert poll.call_count == 2 + int(expires_during_download)
    expected_key = "RequestId" if stream_name == BULK_STREAM else "ReportRequestId"
    for poll_request in poll.request_history[1:]:
        assert poll_request.json() == {expected_key: "request-1"}
        assert poll_request.headers["Authorization"] == "Bearer test"
        assert poll_request.headers["CustomerAccountId"] == "1"
        assert poll_request.headers["CustomerId"] == "2"


@freeze_time("2023-01-02")
def test_persistent_expiry_is_bounded_and_transient(download_flow, requests_mock):
    stream_name, _, poll_url, poll_response, _ = download_flow
    poll = requests_mock.post(poll_url, json=poll_response(EXPIRED_URL))
    expired = requests_mock.get(EXPIRED_URL, status_code=403, text=EXPIRY_RESPONSE)

    output = read_download(download_flow)

    assert not output.records
    assert output.errors[0].trace.error.failure_type == FailureType.transient_error
    assert (
        output.errors[0].trace.error.message
        == f"The Bing Ads download link for stream '{stream_name}' expired before the file could be downloaded. The sync will retry."
    )
    assert expired.call_count == 2
    assert poll.call_count == 3


@freeze_time("2023-01-02")
@pytest.mark.parametrize(
    "body",
    [
        "<Error><Code>AuthorizationPermissionMismatch</Code></Error>",
        "<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>Signature did not match.</AuthenticationErrorDetail></Error>",
    ],
)
def test_other_forbidden_downloads_remain_config_errors(download_flow, requests_mock, body):
    _, _, poll_url, poll_response, _ = download_flow
    requests_mock.post(poll_url, json=poll_response(EXPIRED_URL))
    forbidden = requests_mock.get(EXPIRED_URL, status_code=403, text=body)

    output = read_download(download_flow)

    assert not output.records
    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    assert "Forbidden" in output.errors[0].trace.error.message
    assert forbidden.call_count == 1
