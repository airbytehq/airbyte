# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net:443/download-url"

# What Azure Blob Storage answers once the pre-signed (SAS) download URL handed out by Bing Ads is past its expiry.
EXPIRED_URL_RESPONSE = {
    "headers": {"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"},
    "text": (
        '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
        "<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly "
        "including the signature.\nRequestId:00000000-0000-0000-0000-000000000000\nTime:2026-01-01T20:23:43.0000000Z</Message>"
        "<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Thu, 01 Jan 2026 19:41:55 GMT] - "
        "Expiry [Thu, 01 Jan 2026 20:06:55 GMT] - Current [Thu, 01 Jan 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"
    ),
}
# Any other 403 from the download host, e.g. a signature that does not grant read access to the file.
OTHER_FORBIDDEN_RESPONSE = {
    "headers": {"x-ms-error-code": "AuthorizationPermissionMismatch", "Content-Type": "application/xml"},
    "text": (
        '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthorizationPermissionMismatch</Code>'
        "<Message>This request is not authorized to perform this operation using this permission.</Message></Error>"
    ),
}

EXPIRED_URL_FAILURE = (FailureType.transient_error, "Bing Ads file download URL is expired.")
OTHER_FORBIDDEN_FAILURE = (FailureType.transient_error, "Bing Ads file download URL is rejected by Azure Blob Storage.")


def _mock_completed_job(requests_mock, stream_name: str) -> None:
    """Mocks one account whose bulk or report job completes and points at DOWNLOAD_URL."""
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 10, "LastModifiedTime": "2022-02-02T22:22:22"}]},
    )
    if "report" in stream_name:
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
            json={"ReportRequestId": "report_request_id"},
        )
        requests_mock.post(
            "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
            json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": DOWNLOAD_URL}},
        )
    else:
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
            json={"DownloadRequestId": "download_request_id"},
        )
        requests_mock.post(
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
            json={"RequestStatus": "Completed", "ResultFileUrl": DOWNLOAD_URL, "PercentComplete": 100},
        )


@pytest.mark.parametrize("stream_name", ["keywords", "ad_performance_report_daily"])
@pytest.mark.parametrize(
    "download_response, expected_failure",
    [
        pytest.param(EXPIRED_URL_RESPONSE, EXPIRED_URL_FAILURE, id="expired_download_url"),
        pytest.param(OTHER_FORBIDDEN_RESPONSE, OTHER_FORBIDDEN_FAILURE, id="other_403"),
    ],
)
def test_forbidden_file_download_fails_stream_without_retry(
    stream_name, download_response, expected_failure, config, mock_auth_token, mock_user_query, requests_mock
):
    _mock_completed_job(requests_mock, stream_name)
    download = requests_mock.get(DOWNLOAD_URL, status_code=403, **download_response)

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog, expecting_exception=True)

    assert output.records == []
    stream_errors = [error.trace.error for error in output.errors if error.trace.error.stream_descriptor]
    assert [(error.stream_descriptor.name, error.failure_type, error.message) for error in stream_errors] == [
        (stream_name, *expected_failure)
    ]
    # Resending the same signed URL cannot succeed, so the file is requested once.
    assert download.call_count == 1
