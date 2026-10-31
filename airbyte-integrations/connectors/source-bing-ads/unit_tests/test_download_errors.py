# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from io import BytesIO
from unittest.mock import Mock

import pytest
import requests
from conftest import find_stream

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


DOWNLOAD_URL = "https://bingadsappsstorageprod.blob.core.windows.net/download?sig=fake-signature"
TIME_WINDOW_ERROR = (
    "<Error><Code>AuthenticationFailed</Code>"
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [2026-10-30T00:00:00Z] - Expiry [2026-10-30T00:10:00Z] - Current [2026-10-30T00:20:00Z]"
    "</AuthenticationErrorDetail></Error>"
)


@pytest.fixture(params=["account_performance_report_daily", "account_performance_report_hourly", "app_install_ads"])
def download_requester(request, config, mock_auth_token, requests_mock):
    stream = find_stream(request.param, config)
    slicer = stream.retriever.stream_slicer if hasattr(stream, "retriever") else stream._stream_partition_generator._stream_slicer
    factory = slicer._job_orchestrator_factory
    closure = dict(zip(factory.__code__.co_freevars, (cell.cell_contents for cell in factory.__closure__)))
    requests_mock.post(
        "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll",
        json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": DOWNLOAD_URL}},
    )
    return closure["job_repository"].download_retriever.requester


def download_slice() -> StreamSlice:
    return StreamSlice(
        partition={"account_id": "1"},
        cursor_slice={},
        extra_fields={
            "ParentCustomerId": "2",
            "creation_response": {"ReportRequestId": "report-request"},
            "download_target": DOWNLOAD_URL,
        },
    )


def test_download_time_window_error_is_transient(download_requester, requests_mock):
    download = requests_mock.get(DOWNLOAD_URL, status_code=403, text=TIME_WINDOW_ERROR)

    with pytest.raises(AirbyteTracedException) as raised:
        download_requester.send_request(stream_slice=download_slice())

    assert raised.value.failure_type == FailureType.transient_error
    assert raised.value.message == "Bing Ads file download URL is outside its validity window."
    assert "sig=" not in raised.value.message
    assert "Signature not valid in the specified time frame" in raised.value.internal_message
    assert download.call_count == 1


@pytest.mark.parametrize(
    "body",
    [
        "<Error><Code>AuthorizationPermissionMismatch</Code><Message>Permission denied.</Message></Error>",
        "<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>Signature did not match.</AuthenticationErrorDetail></Error>",
        TIME_WINDOW_ERROR.replace("AuthenticationFailed", "AuthorizationPermissionMismatch"),
        "<Error><Code>AuthenticationFailed</Code></Error>",
        "Forbidden",
        "",
        "<Error><Code>AuthenticationFailed</Code>",
    ],
)
def test_other_download_forbidden_errors_remain_config_errors(download_requester, requests_mock, body):
    download = requests_mock.get(DOWNLOAD_URL, status_code=403, text=body)

    with pytest.raises(AirbyteTracedException) as raised:
        download_requester.send_request(stream_slice=download_slice())

    assert raised.value.failure_type == FailureType.config_error
    assert download.call_count == 1


def test_download_success_preserves_streaming_body(download_requester):
    response = requests.Response()
    response.status_code = 200
    response.raw = Mock(wraps=BytesIO(b"streamed compressed file"))

    resolution = download_requester.error_handler.interpret_response(response)

    assert resolution.response_action == ResponseAction.SUCCESS
    response.raw.read.assert_not_called()
    assert not response._content_consumed


@pytest.mark.parametrize("status_code", [401, 429, 500])
def test_other_download_statuses_keep_default_handling(download_requester, status_code):
    response = requests.Response()
    response.status_code = status_code
    response._content = TIME_WINDOW_ERROR.encode()

    resolution = download_requester.error_handler.interpret_response(response)

    assert resolution == DefaultErrorHandler(config={}, parameters={}).interpret_response(response)


@pytest.mark.parametrize(
    "body",
    [
        TIME_WINDOW_ERROR.replace("<Error>", '<Error xmlns="http://schemas.microsoft.com/windowsazure">'),
        TIME_WINDOW_ERROR.replace("2026-10-30T00:20:00Z", "2026-10-29T23:59:00Z"),
    ],
)
def test_namespaced_and_not_yet_valid_sas_errors(components_module, body):
    response = requests.Response()
    response.status_code = 403
    response._content = body.encode()

    resolution = components_module.BingAdsDownloadErrorHandler(config={}, parameters={}).interpret_response(response)

    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.transient_error


def test_download_connection_error_keeps_default_handling(components_module):
    error = requests.ConnectionError("Connection reset.")
    handler = components_module.BingAdsDownloadErrorHandler(config={}, parameters={})

    assert handler.interpret_response(error) == DefaultErrorHandler(config={}, parameters={}).interpret_response(error)
