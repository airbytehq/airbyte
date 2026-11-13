# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import gzip
import zipfile
from io import BytesIO
from typing import Any, Callable

import pytest
from conftest import get_source
from freezegun import freeze_time
from requests_mock import Mocker
from requests_mock.adapter import _Matcher

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


STALE_URL = "https://storage.example.com/download?sig=stale"
FRESH_URL = "https://storage.example.com/download?sig=fresh"
EXPIRY_RESPONSE = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame.</AuthenticationErrorDetail></Error>"
)
STREAMS = ["app_install_ads", "account_performance_report_daily"]
DownloadRead = tuple[Callable[..., EntrypointOutput], str, _Matcher, dict[str, str], bytes, str]


@pytest.fixture(params=STREAMS)
def download_read(
    request: pytest.FixtureRequest, requests_mock: Mocker, config: dict[str, Any], mock_auth_token: object, mock_user_query: object
) -> DownloadRead:
    stream_name = request.param
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
    )
    if stream_name == "app_install_ads":
        creation_url = "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds"
        poll_url = "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query"
        creation = {"DownloadRequestId": "request-id"}
        expected_body = {"RequestId": "request-id"}
        file_content = gzip.compress(b"Type,Id,Modified Time\nApp Install Ad,42,01/01/2024 00:00:00.000\n")
        record_id = "Id"
    else:
        creation_url = "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit"
        poll_url = "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll"
        creation = {"ReportRequestId": "request-id"}
        expected_body = {"ReportRequestId": "request-id"}
        archive = BytesIO()
        with zipfile.ZipFile(archive, "w") as zipped:
            zipped.writestr("report.csv", "AccountId,TimePeriod\n42,2024-01-01\n")
        file_content = archive.getvalue()
        record_id = "AccountId"

    def status(url: str) -> dict[str, Any]:
        if stream_name == "app_install_ads":
            return {"RequestStatus": "Completed", "ResultFileUrl": url}
        return {"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": url}}

    requests_mock.post(creation_url, json=creation)
    poll = requests_mock.post(poll_url, [{"json": status(STALE_URL)}, {"json": status(STALE_URL)}, {"json": status(FRESH_URL)}])
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    config = {**config, "reports_start_date": "2024-01-01"}

    def run(expecting_exception: bool = False) -> EntrypointOutput:
        return read(get_source(config), config, catalog, expecting_exception=expecting_exception)

    return run, stream_name, poll, expected_body, file_content, record_id


@freeze_time("2024-01-02")
def test_expired_download_repolls_and_emits_records(download_read: DownloadRead, requests_mock: Mocker) -> None:
    run, _, poll, expected_body, file_content, record_id = download_read
    stale = requests_mock.get(STALE_URL, status_code=403, text=EXPIRY_RESPONSE)
    fresh = requests_mock.get(FRESH_URL, content=file_content)

    output = run()

    assert output.errors == []
    assert [record.record.data[record_id] for record in output.records] == [42]
    assert stale.call_count == 1
    assert fresh.call_count == 1
    assert poll.call_count == 3
    assert [request.json() for request in poll.request_history] == [expected_body] * 3
    for request in poll.request_history[1:]:
        assert request.headers["Authorization"] == "Bearer test"
        assert request.headers["CustomerId"] == "2"
        assert request.headers["CustomerAccountId"] == "1"


@freeze_time("2024-01-02")
def test_persistent_expiry_is_bounded_and_transient(download_read: DownloadRead, requests_mock: Mocker) -> None:
    run, stream_name, poll, _, _, _ = download_read
    stale = requests_mock.get(STALE_URL, status_code=403, text=EXPIRY_RESPONSE)
    fresh = requests_mock.get(FRESH_URL, status_code=403, text=EXPIRY_RESPONSE)

    output = run(expecting_exception=True)

    assert output.records == []
    errors = [message.trace.error for message in output.errors if message.trace.error.stream_descriptor]
    assert [(error.failure_type, error.message) for error in errors] == [
        (FailureType.transient_error, f"The Bing Ads download link for stream '{stream_name}' expired.")
    ]
    assert stale.call_count == 1
    assert fresh.call_count == 1
    assert poll.call_count == 3


@freeze_time("2024-01-02")
def test_unrelated_forbidden_is_not_retried(download_read: DownloadRead, requests_mock: Mocker) -> None:
    run, _, poll, _, _, _ = download_read
    download = requests_mock.get(STALE_URL, status_code=403, text="<Error><Code>AuthorizationPermissionMismatch</Code></Error>")

    output = run(expecting_exception=True)

    assert output.records == []
    assert [message.trace.error.failure_type for message in output.errors if message.trace.error.stream_descriptor] == [
        FailureType.config_error
    ]
    assert download.call_count == 1
    assert poll.call_count == 2
