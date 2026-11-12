# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


EXPIRED_RESPONSE = """<?xml version="1.0" encoding="utf-8"?>
<Error><Code>AuthenticationFailed</Code><Message>Server failed to authenticate the request.
Make sure the value of Authorization header is formed correctly including the signature.
RequestId:test-request
Time:2026-11-10T20:23:43Z</Message><AuthenticationErrorDetail>Signature not valid in the specified time frame:
Start [Tue, 10 Nov 2026 19:41:55 GMT] - Expiry [Tue, 10 Nov 2026 20:06:55 GMT] -
Current [Tue, 10 Nov 2026 20:23:43 GMT]</AuthenticationErrorDetail></Error>"""


@freeze_time("2026-11-10")
@pytest.mark.parametrize("stream_name", ["app_install_ads", "ad_performance_report_daily"])
@pytest.mark.parametrize("expired", [True, False], ids=["expired_signature", "unrelated_forbidden"])
def test_download_errors(stream_name, expired, config, mock_auth_token, mock_user_query, mock_account_query, requests_mock):
    download_url = "https://bingadsappsstorageprod.blob.core.windows.net/bulkdownloadresultfiles/report.gz?sig=test"
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        json={"Accounts": [{"Id": 1, "LastModifiedTime": "2022-02-02T22:22:22"}]},
    )
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/Campaigns/DownloadByAccountIds",
        json={"DownloadRequestId": "bulk-request"},
    )
    requests_mock.post(
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query",
        json={"RequestStatus": "Completed", "ResultFileUrl": download_url},
    )
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Submit",
        json={"ReportRequestId": "report-request"},
    )
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
        json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": download_url}},
    )
    download = requests_mock.get(
        download_url,
        status_code=403,
        headers={"x-ms-error-code": "AuthenticationFailed" if expired else "AuthorizationFailure"},
        text=EXPIRED_RESPONSE if expired else "<Error><Code>AuthorizationFailure</Code></Error>",
    )

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog, expecting_exception=True)

    error = output.errors[0].trace.error
    assert error.failure_type.value == ("transient_error" if expired else "config_error")
    assert error.message == (
        "Bing Ads file download URL is expired." if expired else "Forbidden. You don't have permission to access this resource."
    )
    assert download.call_count == 1
    if expired:
        assert EXPIRED_RESPONSE in error.internal_message
