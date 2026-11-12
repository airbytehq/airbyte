# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@freeze_time("2024-01-02")
@pytest.mark.parametrize("stream_name", ["app_install_ads", "ad_performance_report_daily"])
@pytest.mark.parametrize(
    "body, expected_failure",
    [
        (
            '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
            "<Message>Server failed to authenticate the request.</Message>"
            "<AuthenticationErrorDetail>Signature not valid in the specified time frame</AuthenticationErrorDetail></Error>",
            FailureType.transient_error,
        ),
        ("<Error><Code>AuthorizationPermissionMismatch</Code></Error>", FailureType.config_error),
        ("", FailureType.config_error),
        ("<Error><Code>AuthenticationFailed</Code><Message>Invalid signature</Message></Error>", FailureType.config_error),
    ],
)
def test_download_errors(config, stream_name, body, expected_failure):
    config["reports_start_date"] = "2024-01-01"
    download_url = "https://example.blob.core.windows.net/report"
    with HttpMocker() as http_mocker, requests_mock.Mocker(real_http=True) as api_mocker:

        def post(url, response):
            api_mocker.post(url, json=response)

        post("https://login.microsoftonline.com/common/oauth2/v2.0/token", {"access_token": "test", "expires_in": 3600})
        post("https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/User/Query", {"User": {"Id": 1}})
        post(
            "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
            {"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
        )
        if stream_name == "app_install_ads":
            post("https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds", {"DownloadRequestId": "request"})
            post(
                "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
                {"RequestStatus": "Completed", "ResultFileUrl": download_url},
            )
        else:
            post("https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit", {"ReportRequestId": "request"})
            post(
                "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
                {"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": download_url}},
            )
        http_mocker.get(HttpRequest(url=download_url), HttpResponse(body, 403))
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog, expecting_exception=True)

    assert not output.records
    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type == expected_failure
    if expected_failure == FailureType.transient_error:
        assert error.message == "The Bing Ads download link expired before the file could be downloaded. The sync will retry."
    else:
        assert "You don't have permission to access this resource" in error.message
