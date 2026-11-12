# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import ANY

import pytest
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


EXPIRED_SAS_XML = """<?xml version="1.0" encoding="utf-8"?>
<Error><Code>AuthenticationFailed</Code>
<Message>Server failed to authenticate the request.</Message>
<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Thu, 12 Nov 2026 00:00:00 GMT] - Expiry [Thu, 12 Nov 2026 00:10:00 GMT] - Current [Thu, 12 Nov 2026 00:20:00 GMT]</AuthenticationErrorDetail></Error>"""
STORAGE_URL = "https://bingadsappsstorageprod.blob.core.windows.net:443/download-url"


@freeze_time("2024-01-02")
@pytest.mark.parametrize("stream_name", ["keywords", "ad_performance_report_daily"], ids=["bulk", "report"])
@pytest.mark.parametrize(
    "body,failure_type,message",
    [
        (EXPIRED_SAS_XML, "transient_error", "Bing Ads file download URL is expired."),
        (
            "<Error><Code>AuthenticationFailed</Code><Message>Signature did not match.</Message></Error>",
            "config_error",
            "Forbidden. You don't have permission to access this resource.",
        ),
        ("", "config_error", "Forbidden. You don't have permission to access this resource."),
    ],
    ids=["expired", "other-403", "empty-403"],
)
def test_download_error(stream_name, body, failure_type, message, config):
    config["reports_start_date"] = "2024-01-01"
    config["client_secret"] = "test-secret"
    is_report = stream_name == "ad_performance_report_daily"
    with HttpMocker() as http_mocker:

        def post(url, payload, request_body):
            request = HttpRequest(url=url, body=request_body)
            http_mocker.post(request, HttpResponse(json.dumps(payload)))
            return request

        post("https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/User/Query", {"User": {"Id": 1}}, {"UserId": None})
        post(
            "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
            {"Accounts": [{"Id": 1, "ParentCustomerId": 2, "LastModifiedTime": "2024-01-01T00:00:00"}]},
            {
                "PageInfo": {"Index": 0, "Size": 1000},
                "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "1"}],
                "ReturnAdditionalFields": "TaxCertificate,AccountMode",
            },
        )
        if is_report:
            post(
                "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
                {"ReportRequestId": "report-id"},
                {"ReportRequest": ANY},
            )
            poll_request = post(
                "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
                {"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": STORAGE_URL}},
                {"ReportRequestId": "report-id"},
            )
        else:
            post(
                "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
                {"DownloadRequestId": "bulk-id"},
                {
                    "AccountIds": ["1"],
                    "DataScope": "EntityData",
                    "DownloadEntities": ["Keywords"],
                    "DownloadFileType": "Csv",
                    "FormatVersion": "6.0",
                    "CompressionType": "GZip",
                    "LastSyncTimeInUTC": "2024-01-01T00:00:00.000+00:00",
                },
            )
            poll_request = post(
                "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
                {"RequestStatus": "Completed", "ResultFileUrl": STORAGE_URL, "PercentComplete": 100},
                {"RequestId": "bulk-id"},
            )
        download_request = HttpRequest(url=STORAGE_URL)
        http_mocker.get(
            download_request,
            HttpResponse(body, 403, headers={"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"}),
        )
        post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            {"access_token": "test", "expires_in": 3600, "refresh_token": "test"},
            "grant_type=refresh_token&client_id=fake_client_id&client_secret=test-secret"
            "&refresh_token=fake_refresh_token&scope=https%3A%2F%2Fads.microsoft.com%2Fmsads.manage+offline_access",
        )
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog, expecting_exception=True)

        http_mocker.assert_number_of_calls(download_request, 1)
        http_mocker.assert_number_of_calls(poll_request, 1)
        error = output.errors[0].trace.error
        assert error.failure_type.value == failure_type
        assert error.message == message
