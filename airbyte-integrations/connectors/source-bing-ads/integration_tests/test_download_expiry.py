# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mocked connector reads for the deployed CDK 7.47.0 runtime, which supplies creation_response in download slices."""

import gzip
import zipfile
from collections import Counter
from io import BytesIO

import pytest
from freezegun import freeze_time
from unit_tests.conftest import config_fixture, get_source, mock_auth_token_fixture, mock_user_query_fixture, patch_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


EXPIRED_RESPONSE = (
    "<Error><Code>AuthenticationFailed</Code><Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame.</AuthenticationErrorDetail></Error>"
)
STALE_URL = "https://storage.blob.core.windows.net/download?sig=stale"
FRESH_URL = "https://storage.blob.core.windows.net/download?sig=fresh"
STREAMS = ["app_install_ads", "account_performance_report_daily"]


def download_payload(stream_name, account_id):
    if stream_name == "app_install_ads":
        return gzip.compress(f"Type,Id,Modified Time\nApp Install Ad,{account_id},01/01/2023 00:00:00.000\n".encode())
    archive = BytesIO()
    with zipfile.ZipFile(archive, "w") as report:
        report.writestr("report.csv", f"TimePeriod,AccountId\n2023-01-01,{account_id}\n")
    return archive.getvalue()


@pytest.fixture(params=STREAMS)
def download_case(request, requests_mock, config, mock_auth_token, mock_user_query):
    stream_name = request.param
    bulk = stream_name == "app_install_ads"
    config["reports_start_date"] = "2023-01-01"
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 99, "LastModifiedTime": "2022-02-02T22:22:22"}]},
    )
    if bulk:
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
            json={"DownloadRequestId": "job-1"},
        )
        poll_url = "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query"
    else:
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
            json={"ReportRequestId": "job-1"},
        )
        poll_url = "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll"

    def poll_response(url):
        if bulk:
            return {"RequestStatus": "Completed", "ResultFileUrl": url}
        return {"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": url}}

    return stream_name, poll_url, poll_response


def read_download(config, stream_name):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog, expecting_exception=True)


@freeze_time("2023-01-02")
def test_expired_download_repolls_and_emits_records(download_case, requests_mock, config):
    stream_name, poll_url, poll_response = download_case
    bulk = stream_name == "app_install_ads"
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={
            "Accounts": [
                {"Id": account_id, "ParentCustomerId": account_id + 98, "LastModifiedTime": "2022-02-02T22:22:22"} for account_id in [1, 2]
            ]
        },
    )
    creation_url = (
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds"
        if bulk
        else "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit"
    )

    def respond_to_creation(request, context):
        account_id = request.headers["CustomerAccountId"].strip("'")
        return {"DownloadRequestId" if bulk else "ReportRequestId": f"job-{account_id}"}

    requests_mock.post(creation_url, json=respond_to_creation)
    poll_counts = Counter()
    request_key = "RequestId" if bulk else "ReportRequestId"

    def respond_to_poll(request, context):
        job_id = request.json()[request_key].strip("'")
        account_id = int(job_id.removeprefix("job-"))
        poll_counts[account_id] += 1
        url = STALE_URL if poll_counts[account_id] <= 2 else FRESH_URL
        return poll_response(f"{url}-{account_id}")

    polls = requests_mock.post(poll_url, json=respond_to_poll)
    stale_downloads = [
        requests_mock.get(f"{STALE_URL}-{account_id}", status_code=403, text=EXPIRED_RESPONSE, complete_qs=True) for account_id in [1, 2]
    ]
    fresh_downloads = [
        requests_mock.get(f"{FRESH_URL}-{account_id}", content=download_payload(stream_name, account_id), complete_qs=True)
        for account_id in [1, 2]
    ]

    output = read_download(config, stream_name)

    assert output.errors == [], [error.trace.error.internal_message for error in output.errors]
    id_field = "Id" if stream_name == "app_install_ads" else "AccountId"
    assert sorted(record.record.data[id_field] for record in output.records) == [1, 2]
    assert [download.call_count for download in stale_downloads] == [1, 1]
    assert [download.call_count for download in fresh_downloads] == [1, 1]
    assert polls.call_count == 6
    assert poll_counts == {1: 3, 2: 3}
    for request in polls.request_history:
        account_id = int(request.headers["CustomerAccountId"].strip("'"))
        assert request.json() == {request_key: f"job-{account_id}"}
        assert request.headers["CustomerId"].strip("'") == str(account_id + 98)
        assert request.headers["DeveloperToken"] == config["developer_token"]
        assert request.headers["Authorization"].startswith("Bearer ")


@freeze_time("2023-01-02")
def test_persistent_download_expiry_is_transient_and_bounded(download_case, requests_mock, config):
    stream_name, poll_url, poll_response = download_case
    polls = requests_mock.post(poll_url, json=poll_response(STALE_URL))
    download = requests_mock.get(STALE_URL, status_code=403, text=EXPIRED_RESPONSE, complete_qs=True)

    output = read_download(config, stream_name)

    assert output.records == []
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.transient_error
    assert error.message == f"Bing Ads download link for stream '{stream_name}' is expired."
    assert EXPIRED_RESPONSE in error.internal_message
    assert "sig=stale" not in error.message
    assert download.call_count == 2
    assert polls.call_count == 3


@freeze_time("2023-01-02")
@pytest.mark.parametrize(
    "body",
    [
        "<Error><Code>AuthorizationPermissionMismatch</Code><Message>Permission denied.</Message></Error>",
        "<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>Signature did not match.</AuthenticationErrorDetail></Error>",
    ],
)
def test_other_download_403_remains_config_error(download_case, requests_mock, config, body):
    stream_name, poll_url, poll_response = download_case
    requests_mock.post(poll_url, json=poll_response(STALE_URL))
    download = requests_mock.get(STALE_URL, status_code=403, text=body, complete_qs=True)

    output = read_download(config, stream_name)

    assert output.records == []
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert error.message == DEFAULT_ERROR_MAPPING[403].error_message
    assert download.call_count == 1
