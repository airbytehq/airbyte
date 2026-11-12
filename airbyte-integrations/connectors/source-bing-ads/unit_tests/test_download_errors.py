# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest
import requests
from components import BingAdsDownloadErrorHandler
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


@freeze_time("2024-01-01")
@pytest.mark.parametrize("stream_name", ["app_install_ads", "ad_performance_report_daily"])
@pytest.mark.parametrize("expired", [True, False])
def test_download_forbidden(stream_name, expired, config, mock_auth_token, mock_user_query, mock_account_query, requests_mock):
    download_url = "https://bingadsappsstorageprod.blob.core.windows.net/download-url"
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
    body = (
        '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
        "<Message>Server failed to authenticate the request.</Message>"
        "<AuthenticationErrorDetail>Signature not valid in the specified time frame.</AuthenticationErrorDetail></Error>"
        if expired
        else "<Error><Code>AuthorizationFailure</Code><Message>Forbidden</Message></Error>"
    )
    download = requests_mock.get(download_url, status_code=403, text=body, headers={"Content-Type": "application/xml"})
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config, catalog, expecting_exception=True)

    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type == (FailureType.transient_error if expired else FailureType.config_error)
    if expired:
        assert "The Bing Ads download link expired before the file could be downloaded. The sync will retry." in error.message
    else:
        assert "Forbidden" in error.message
    assert 1 <= download.call_count <= 3


@pytest.mark.parametrize("status", [200, 204, 403, 429, 500])
def test_download_handler_preserves_defaults(status):
    response = requests.Response()
    response.status_code = status
    response._content = b""
    handler = BingAdsDownloadErrorHandler(config={}, parameters={})
    assert handler.interpret_response(response) == DefaultErrorHandler(config={}, parameters={}).interpret_response(response)


def test_successful_download_body_is_not_read():
    response = requests.Response()
    response.status_code = 200
    response.raw = MagicMock()
    response.raw.read.side_effect = AssertionError("Successful download body must remain streamed")
    result = BingAdsDownloadErrorHandler(config={}, parameters={}).interpret_response(response)
    assert result.response_action == ResponseAction.SUCCESS
    response.raw.read.assert_not_called()
