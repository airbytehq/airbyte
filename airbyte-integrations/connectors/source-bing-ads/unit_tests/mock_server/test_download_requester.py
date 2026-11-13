# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


EXPIRED_RESPONSE = (
    "<Error><Code>AuthenticationFailed</Code>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame.</AuthenticationErrorDetail></Error>"
)
STALE_URL = "https://storage.blob.core.windows.net/download?sig=stale"
FRESH_URL = "https://storage.blob.core.windows.net/download?sig=fresh"


@pytest.fixture(params=[False, True], ids=["report", "bulk"])
def download_request(request, components_module):
    bulk = request.param
    authenticator = MagicMock()
    authenticator.get_auth_header.return_value = {"Authorization": "Bearer test"}
    requester = components_module.BingAdsReportDownloadRequester(
        name="job download - test_stream",
        config={"developer_token": "test-developer-token"},
        parameters={},
        url_base="{{ download_target }}",
        http_method="GET",
        report_poll_authenticator=authenticator,
    )
    requester.bulk_download = bulk
    stream_slice = StreamSlice(
        partition={"account_id": "1"},
        cursor_slice={},
        extra_fields={
            "ParentCustomerId": "99",
            "creation_response": {"DownloadRequestId" if bulk else "ReportRequestId": "job-1"},
            "download_target": STALE_URL,
        },
    )
    poll_url = (
        "https://bulk.api.bingads.microsoft.com/Bulk/v13/BulkDownloadStatus/Query"
        if bulk
        else "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll"
    )

    def poll_response(url):
        return {"ResultFileUrl": url} if bulk else {"ReportRequestStatus": {"ReportDownloadUrl": url}}

    return requester, stream_slice, poll_url, poll_response


def test_expired_download_refreshes_url(download_request, requests_mock):
    requester, stream_slice, poll_url, poll_response = download_request
    polls = requests_mock.post(poll_url, [{"json": poll_response(STALE_URL)}, {"json": poll_response(FRESH_URL)}])
    stale = requests_mock.get(STALE_URL, status_code=403, text=EXPIRED_RESPONSE, complete_qs=True)
    fresh = requests_mock.get(FRESH_URL, content=b"downloaded file", complete_qs=True)

    response = requester.send_request(stream_slice=stream_slice)

    assert response.content == b"downloaded file"
    assert stale.call_count == fresh.call_count == 1
    assert polls.call_count == 2
    for request in polls.request_history:
        assert request.json() == {"RequestId" if requester.bulk_download else "ReportRequestId": "job-1"}
        assert request.headers["CustomerAccountId"] == "1"
        assert request.headers["CustomerId"] == "99"
        assert request.headers["Authorization"] == "Bearer test"


def test_repeated_expiry_is_transient_with_bounded_downloads(download_request, requests_mock):
    requester, stream_slice, poll_url, poll_response = download_request
    polls = requests_mock.post(poll_url, json=poll_response(STALE_URL))
    download = requests_mock.get(STALE_URL, status_code=403, text=EXPIRED_RESPONSE, complete_qs=True)

    with pytest.raises(AirbyteTracedException) as error:
        requester.send_request(stream_slice=stream_slice)

    assert error.value.failure_type == FailureType.transient_error
    assert error.value.message == "Bing Ads download link for stream 'test_stream' is expired."
    assert EXPIRED_RESPONSE in error.value.internal_message
    assert download.call_count == 2
    assert polls.call_count == 2
