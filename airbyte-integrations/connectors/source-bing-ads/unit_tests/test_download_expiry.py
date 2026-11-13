# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from components import BingAdsReportDownloadRequester

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.auth.token_provider import InterpolatedStringTokenProvider
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


EXPIRED_SAS = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame.</AuthenticationErrorDetail></Error>"
)
STALE_URL = "https://example.blob.core.windows.net/download?sig=stale"
FRESH_URL = "https://example.blob.core.windows.net/download?sig=fresh"
STREAMS = ["app_install_ads", "account_performance_report_daily"]


@pytest.fixture
def download(config, requests_mock):
    def setup(stream_name, *, recover=False, error=EXPIRED_SAS):
        bulk = stream_name == "app_install_ads"
        requester = BingAdsReportDownloadRequester(
            name=f"job download - {stream_name}",
            config=config,
            parameters={},
            url_base="{{ download_target }}",
            http_method="GET",
            report_poll_authenticator=BearerAuthenticator(
                token_provider=InterpolatedStringTokenProvider(api_token="test", config=config, parameters={}),
                config=config,
                parameters={},
            ),
        )
        if bulk:
            requester.poll_url = "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query"
            requester.creation_request_id_field = "DownloadRequestId"
            requester.poll_request_id_field = "RequestId"
            requester.download_url_field = "ResultFileUrl"
            requester.poll_response_field = None
        poll_url = (
            "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query"
            if bulk
            else "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll"
        )

        def status(url):
            return (
                {"RequestStatus": "Completed", "ResultFileUrl": url}
                if bulk
                else {"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": url}}
            )

        poll = requests_mock.post(poll_url, [{"json": status(STALE_URL)}, {"json": status(FRESH_URL if recover else STALE_URL)}])
        stale = requests_mock.get(STALE_URL, status_code=403, text=error, headers={"Content-Type": "application/xml"})
        fresh = requests_mock.get(FRESH_URL, content=b"downloaded file")
        stream_slice = StreamSlice(
            partition={"account_id": 1},
            cursor_slice={},
            extra_fields={
                "ParentCustomerId": 2,
                "creation_response": {"DownloadRequestId" if bulk else "ReportRequestId": "request-1"},
                "download_target": STALE_URL,
            },
        )
        return requester, stream_slice, poll, stale, fresh

    return setup


@pytest.mark.parametrize("stream_name", STREAMS)
def test_download_refreshes_expired_link(download, stream_name):
    requester, stream_slice, poll, stale, fresh = download(stream_name, recover=True)

    response = requester.send_request(stream_slice=stream_slice)

    assert response.content == b"downloaded file"
    assert response.url == FRESH_URL
    assert stale.call_count == 1
    assert fresh.call_count == 1
    assert poll.call_count == 2
    for request in poll.request_history:
        assert request.json() == {"RequestId" if stream_name == "app_install_ads" else "ReportRequestId": "request-1"}
        assert request.headers["Authorization"] == "Bearer test"
        assert request.headers["CustomerAccountId"] == "1"
        assert request.headers["CustomerId"] == "2"


@pytest.mark.parametrize("stream_name", STREAMS)
def test_download_reports_persistent_expiry_as_transient(download, stream_name):
    requester, stream_slice, poll, stale, fresh = download(stream_name)

    with pytest.raises(AirbyteTracedException) as raised:
        requester.send_request(stream_slice=stream_slice)

    error = raised.value
    assert error.failure_type == FailureType.transient_error
    assert error.message == f"The Bing Ads download link for stream '{stream_name}' is expired."
    assert "AuthenticationFailed" in error.internal_message
    assert "Signature not valid in the specified time frame" in error.internal_message
    assert stale.call_count == 2
    assert fresh.call_count == 0
    assert poll.call_count == 2


@pytest.mark.parametrize("stream_name", STREAMS)
@pytest.mark.parametrize(
    "body",
    [
        "<Error><Code>AuthorizationPermissionMismatch</Code><Message>Permission denied.</Message></Error>",
        "<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>Signature did not match.</AuthenticationErrorDetail></Error>",
    ],
)
def test_download_keeps_non_expiry_403_as_config_error(download, stream_name, body):
    requester, stream_slice, poll, stale, fresh = download(stream_name, error=body)

    with pytest.raises(AirbyteTracedException) as raised:
        requester.send_request(stream_slice=stream_slice)

    error = raised.value
    assert error.failure_type == FailureType.config_error
    assert error.message.endswith("Forbidden. You don't have permission to access this resource.")
    assert stale.call_count == 1
    assert fresh.call_count == 0
