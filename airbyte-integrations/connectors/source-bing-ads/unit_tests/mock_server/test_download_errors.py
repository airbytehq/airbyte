# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import io
import zipfile

import pytest
from freezegun import freeze_time
from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


EXPIRED_LINK = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Expiry [Mon, 06 May 2024 00:00:00 GMT] - Current [Mon, 06 May 2024 00:05:00 GMT]"
    "</AuthenticationErrorDetail></Error>"
)
STREAMS = ["app_install_ads", "budget_summary_report"]


@pytest.fixture
def download_api(requests_mock, mock_auth_token, mock_user_query):
    def setup(stream_name, body=EXPIRED_LINK, recover=False):
        account_ids = [1, 2] if recover else [1]
        requests_mock.post(
            "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
            json={
                "Accounts": [
                    {"Id": account_id, "ParentCustomerId": 10, "LastModifiedTime": "2024-05-05T00:00:00"} for account_id in account_ids
                ]
            },
        )
        is_bulk = stream_name == "app_install_ads"
        root = (
            "https://bulk.api.bingads.microsoft.com/Bulk/v13"
            if is_bulk
            else "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport"
        )
        creation_key = "DownloadRequestId" if is_bulk else "ReportRequestId"

        def creation_response(request, context):
            payload = request.json()
            account_id = payload["AccountIds"][0] if is_bulk else payload["ReportRequest"]["Scope"]["AccountIds"][0]
            return {creation_key: f"job-{account_id}"}

        requests_mock.post(f"{root}/{'Campaigns/DownloadByAccountIds' if is_bulk else 'Submit'}", json=creation_response)
        old_urls = {account_id: f"https://download.example.com/{account_id}/old?sig=expired" for account_id in account_ids}
        fresh_urls = {account_id: f"https://download.example.com/{account_id}/fresh?sig=renewed" for account_id in account_ids}
        downloads = {
            account_id: requests_mock.get(url, status_code=403, text=body, complete_qs=True) for account_id, url in old_urls.items()
        }

        def status_response(request, context):
            job_id = request.json()["RequestId" if is_bulk else "ReportRequestId"]
            account_id = int(job_id.removeprefix("job-"))
            url = fresh_urls[account_id] if recover and downloads[account_id].called else old_urls[account_id]
            return (
                {"RequestStatus": "Completed", "ResultFileUrl": url}
                if is_bulk
                else {"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": url}}
            )

        polls = requests_mock.post(f"{root}/{'BulkDownloadStatus/Query' if is_bulk else 'Poll'}", json=status_response, complete_qs=True)
        fresh_downloads = {}
        for account_id in account_ids:
            if is_bulk:
                data = f"Type,Id,Modified Time\nApp Install Ad,{123 * account_id},05/05/2024 00:00:00.000\n".encode()
            else:
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w") as archive:
                    archive.writestr("report.csv", f"Date,CampaignId,MonthlyBudget\n5/5/2024,{123 * account_id},10\n")
                data = buffer.getvalue()
            fresh_downloads[account_id] = requests_mock.get(fresh_urls[account_id], content=data, complete_qs=True)
        return downloads, fresh_downloads, polls

    return setup


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", STREAMS)
def test_expired_download_link_has_transient_stream_error(stream_name, config, download_api):
    config["reports_start_date"] = "2024-05-05"
    downloads, fresh_downloads, polls = download_api(stream_name)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog, expecting_exception=True)
    error = next(error.trace.error for error in output.errors if error.trace.error.stream_descriptor)
    assert error.failure_type == FailureType.transient_error
    assert error.message == f"The Bing Ads download link for stream '{stream_name}' expired before the file could be downloaded."
    assert error.internal_message == EXPIRED_LINK
    assert downloads[1].call_count == 2
    assert fresh_downloads[1].call_count == 0
    assert polls.call_count == 3
    assert len(output.records) == 0


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", STREAMS)
def test_expired_download_link_is_refreshed_before_retry(stream_name, config, download_api):
    config["reports_start_date"] = "2024-05-05"
    downloads, fresh_downloads, polls = download_api(stream_name, recover=True)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog)
    assert not output.errors
    assert sorted(record.record.data["Id" if stream_name == "app_install_ads" else "CampaignId"] for record in output.records) == [123, 246]
    assert [downloads[account_id].call_count for account_id in (1, 2)] == [1, 1]
    assert [fresh_downloads[account_id].call_count for account_id in (1, 2)] == [1, 1]
    request_key = "RequestId" if stream_name == "app_install_ads" else "ReportRequestId"
    assert sorted(request.json()[request_key] for request in polls.request_history) == ["job-1"] * 3 + ["job-2"] * 3
    for request in polls.request_history:
        account_id = request.json()[request_key].removeprefix("job-")
        assert request.headers["CustomerAccountId"] == account_id
        assert request.headers["CustomerId"] == "10"
        assert request.headers["DeveloperToken"] == config["developer_token"]
        assert request.headers["Authorization"] == "Bearer test"


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", STREAMS)
@pytest.mark.parametrize(
    "body",
    [
        "Forbidden",
        EXPIRED_LINK.replace("AuthenticationFailed", "AuthorizationPermissionMismatch"),
        EXPIRED_LINK.replace("Signature not valid in the specified time frame", "Signature did not match"),
    ],
)
def test_other_download_forbidden_errors_remain_config_errors(stream_name, body, config, download_api):
    config["reports_start_date"] = "2024-05-05"
    downloads, fresh_downloads, polls = download_api(stream_name, body=body)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog, expecting_exception=True)
    error = next(error.trace.error for error in output.errors if error.trace.error.stream_descriptor)
    assert error.failure_type == FailureType.config_error
    assert error.message == "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource."
    assert downloads[1].call_count == 1
    assert fresh_downloads[1].call_count == 0
    assert len(output.records) == 0
