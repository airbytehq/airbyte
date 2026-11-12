# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/download.csv?sig=test-signature"
EXPIRY_DETAIL = "Signature not valid in the specified time frame"
FORBIDDEN_MESSAGE = DEFAULT_ERROR_MAPPING[403].error_message


@pytest.fixture(params=["keywords", "account_performance_report_daily"])
def download_stream(request: pytest.FixtureRequest, requests_mock: Mocker, mock_auth_token: None, mock_user_query: None) -> str:
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
    )
    if request.param == "keywords":
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
    return request.param


@freeze_time("2024-05-06T12:00:00")
@pytest.mark.parametrize(
    "error_code, detail, include_header, expected_type, expected_message",
    [
        pytest.param(
            "AuthenticationFailed",
            EXPIRY_DETAIL,
            True,
            FailureType.transient_error,
            "Bing Ads file download link is expired.",
            id="expired-sas",
        ),
        pytest.param(
            "AuthenticationFailed",
            EXPIRY_DETAIL,
            False,
            FailureType.transient_error,
            "Bing Ads file download link is expired.",
            id="expired-sas-without-header",
        ),
        pytest.param(
            "AuthorizationPermissionMismatch",
            "Permission denied.",
            True,
            FailureType.config_error,
            FORBIDDEN_MESSAGE,
            id="permission-denied",
        ),
        pytest.param(
            "AuthenticationFailed",
            "The MAC signature found in the HTTP request is not the same as any computed signature.",
            True,
            FailureType.config_error,
            FORBIDDEN_MESSAGE,
            id="invalid-signature",
        ),
    ],
)
def test_download_failure_classification(
    requests_mock: Mocker,
    download_stream: str,
    config: dict[str, str | int],
    error_code: str,
    detail: str,
    include_header: bool,
    expected_type: FailureType,
    expected_message: str,
) -> None:
    config["reports_start_date"] = "2024-05-06"
    download = requests_mock.get(
        DOWNLOAD_URL,
        status_code=403,
        headers={"Content-Type": "application/xml", **({"x-ms-error-code": error_code} if include_header else {})},
        text=f"<Error><Code>{error_code}</Code><Message>Server failed to authenticate the request.</Message>"
        f"<AuthenticationErrorDetail>{detail}</AuthenticationErrorDetail></Error>",
    )
    catalog = CatalogBuilder().with_stream(download_stream, SyncMode.full_refresh).build()

    output = read(get_source(config), config, catalog, expecting_exception=True)

    errors = [
        message.trace.error for message in output.errors if message.trace and message.trace.error and message.trace.error.stream_descriptor
    ]
    assert len(errors) == 1
    assert errors[0].stream_descriptor is not None
    assert errors[0].stream_descriptor.name == download_stream
    assert errors[0].failure_type == expected_type
    assert errors[0].message == expected_message
    assert output.records == []
    assert download.call_count == 1
