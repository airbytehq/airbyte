# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/download?sig=expired"
# Body Azure Blob Storage returns when the pre-signed (SAS) download URL has expired.
EXPIRED_SAS_RESPONSE = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
    "including the signature.\nRequestId:11111111-1111-1111-1111-111111111111\nTime:2024-02-26T00:20:00.0000000Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Mon, 26 Feb 2024 00:00:00 GMT] - "
    "Expiry [Mon, 26 Feb 2024 00:10:00 GMT] - Current [Mon, 26 Feb 2024 00:20:00 GMT]</AuthenticationErrorDetail></Error>"
)
# Body Azure Blob Storage returns for a 403 that is not caused by an expired link.
OTHER_FORBIDDEN_RESPONSE = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationFailure</Code>'
    "<Message>This request is not authorized to perform this operation.</Message></Error>"
)


@pytest.fixture
def single_account(requests_mock: Mocker, mock_auth_token: None, mock_user_query: None) -> None:
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
    )


@pytest.fixture
def completed_bulk_job(requests_mock: Mocker) -> None:
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
        json={"DownloadRequestId": "download-id"},
    )
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
        json={"RequestStatus": "Completed", "ResultFileUrl": DOWNLOAD_URL, "PercentComplete": 100},
    )


@pytest.fixture
def completed_report_job(requests_mock: Mocker) -> None:
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
        json={"ReportRequestId": "report-id"},
    )
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
        json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": DOWNLOAD_URL}},
    )


def _read_with_failing_download(requests_mock: Mocker, config: dict[str, str | int], stream_name: str, response_body: str):
    requests_mock.get(DOWNLOAD_URL, status_code=403, text=response_body)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config, None), config, catalog, None, expecting_exception=True)
    download_attempts = [request for request in requests_mock.request_history if request.url == DOWNLOAD_URL]
    return output, download_attempts


@freeze_time("2024-02-26")
@pytest.mark.parametrize("stream_name", ["labels", "campaign_performance_report_daily"])
def test_expired_download_link_fails_as_transient_error_naming_the_expired_link(
    requests_mock: Mocker,
    single_account: None,
    completed_bulk_job: None,
    completed_report_job: None,
    config: dict[str, str | int],
    stream_name: str,
) -> None:
    config["reports_start_date"] = "2024-02-20"

    output, download_attempts = _read_with_failing_download(requests_mock, config, stream_name, EXPIRED_SAS_RESPONSE)

    assert output.records == []
    # The first trace is the stream-level failure; the CDK then appends a sync-level summary trace.
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.transient_error
    assert (
        error.message == "The Microsoft Advertising (Bing Ads) download link for this stream's file expired before the file could be "
        "downloaded. This is a temporary condition and not a problem with your credentials or permissions. The sync will retry."
    )
    assert error.stream_descriptor.name == stream_name
    # The expired link can never succeed, so it must not be re-requested.
    assert len(download_attempts) == 1


@freeze_time("2024-02-26")
@pytest.mark.parametrize("stream_name", ["labels", "campaign_performance_report_daily"])
def test_forbidden_download_that_is_not_an_expired_link_stays_a_config_error(
    requests_mock: Mocker,
    single_account: None,
    completed_bulk_job: None,
    completed_report_job: None,
    config: dict[str, str | int],
    stream_name: str,
) -> None:
    config["reports_start_date"] = "2024-02-20"

    output, download_attempts = _read_with_failing_download(requests_mock, config, stream_name, OTHER_FORBIDDEN_RESPONSE)

    assert output.records == []
    # The first trace is the stream-level failure; the CDK then appends a sync-level summary trace.
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert error.message == "Forbidden. You don't have permission to access this resource."
    assert len(download_attempts) == 1
