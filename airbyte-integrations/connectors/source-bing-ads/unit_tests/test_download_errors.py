# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import io
from typing import Mapping

import pytest
from conftest import get_source
from requests import Response
from requests_mock import Mocker

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models import CustomRequester, HttpRequester
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester as Requester
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


DOWNLOAD_URL = "https://example.blob.core.windows.net/report?sig=test-signature"
EXPIRY_ERROR = (
    "<Error><Code>AuthenticationFailed</Code>"
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [2026-01-01T00:00:00Z] - Expiry [2026-01-01T00:10:00Z] - Current [2026-01-01T00:20:00Z]"
    "</AuthenticationErrorDetail></Error>"
)
EXPIRY_MESSAGE = "The Bing Ads file download URL is expired or not yet valid."


@pytest.fixture(scope="module")
def resolved_manifest() -> Mapping:
    return get_source({}).resolved_manifest


@pytest.fixture(params=["basic_async_retriever", "basic_bulk_async_retriever"], ids=["report", "bulk"])
def download_requester(request: pytest.FixtureRequest, resolved_manifest: Mapping, config: dict, mocker) -> Requester:
    definition = resolved_manifest["definitions"][request.param]["download_requester"]
    model = CustomRequester if definition["type"] == "CustomRequester" else HttpRequester
    requester = ModelToComponentFactory().create_component(model, definition, config, name=request.param)
    if model is CustomRequester:
        mocker.patch.object(requester, "_get_fresh_download_url", return_value=None)
    return requester


def test_expired_download_is_transient(download_requester: Requester, requests_mock: Mocker) -> None:
    requests_mock.get(DOWNLOAD_URL, status_code=403, text=EXPIRY_ERROR, headers={"Content-Type": "application/xml"})
    stream_slice = StreamSlice(partition={}, cursor_slice={}, extra_fields={"download_target": DOWNLOAD_URL})

    with pytest.raises(AirbyteTracedException) as error:
        download_requester.send_request(stream_slice=stream_slice)

    assert error.value.failure_type == FailureType.transient_error
    assert error.value.message == EXPIRY_MESSAGE
    assert "sig=test-signature" not in error.value.message
    assert requests_mock.call_count == 1


@pytest.mark.parametrize(
    "body",
    [
        "<Error><Code>AuthorizationPermissionMismatch</Code><Message>Permission denied.</Message></Error>",
        "<Error><Code>AuthenticationFailed</Code><Message>The MAC signature is invalid.</Message></Error>",
        '{"error": "Forbidden"}',
        "Forbidden",
        "<Error><Code>AuthenticationFailed</Code>",
        "",
        EXPIRY_ERROR.replace("AuthenticationFailed", "AuthorizationPermissionMismatch"),
    ],
    ids=["permission-mismatch", "other-authentication-failure", "json", "plain-text", "malformed-xml", "empty", "non-expiry-code"],
)
def test_other_download_forbidden_errors_remain_config_errors(download_requester: Requester, requests_mock: Mocker, body: str) -> None:
    requests_mock.get(DOWNLOAD_URL, status_code=403, text=body)
    stream_slice = StreamSlice(partition={}, cursor_slice={}, extra_fields={"download_target": DOWNLOAD_URL})

    with pytest.raises(AirbyteTracedException) as error:
        download_requester.send_request(stream_slice=stream_slice)

    assert error.value.failure_type == FailureType.config_error
    assert requests_mock.call_count == 1


def test_successful_download_is_unchanged(download_requester: Requester, requests_mock: Mocker) -> None:
    requests_mock.get(DOWNLOAD_URL, content=b"downloaded report")
    stream_slice = StreamSlice(partition={}, cursor_slice={}, extra_fields={"download_target": DOWNLOAD_URL})

    response = download_requester.send_request(stream_slice=stream_slice)

    assert response is not None
    assert response.content == b"downloaded report"
    assert requests_mock.call_count == 1


def test_successful_streamed_download_is_not_consumed(download_requester: Requester) -> None:
    response = Response()
    response.status_code = 200
    response.raw = io.BytesIO(b"downloaded report")

    assert download_requester.error_handler is not None
    resolution = download_requester.error_handler.interpret_response(response)

    assert resolution.response_action == ResponseAction.SUCCESS
    assert response.raw.tell() == 0
    assert not response._content_consumed


@pytest.mark.parametrize("status_code", [429, 500])
def test_retryable_download_errors_still_retry(download_requester: Requester, requests_mock: Mocker, status_code: int) -> None:
    requests_mock.get(DOWNLOAD_URL, [{"status_code": status_code}, {"content": b"downloaded report"}])
    stream_slice = StreamSlice(partition={}, cursor_slice={}, extra_fields={"download_target": DOWNLOAD_URL})

    response = download_requester.send_request(stream_slice=stream_slice)

    assert response is not None
    assert response.content == b"downloaded report"
    assert requests_mock.call_count == 2


@pytest.mark.parametrize("retriever", ["basic_async_retriever", "basic_bulk_async_retriever"], ids=["report", "bulk"])
@pytest.mark.parametrize("phase", ["creation_requester", "polling_requester"], ids=["submit", "poll"])
def test_non_download_errors_keep_default_classification(resolved_manifest: Mapping, config: dict, retriever: str, phase: str) -> None:
    definition = resolved_manifest["definitions"][retriever][phase]
    requester = ModelToComponentFactory().create_component(HttpRequester, definition, config, name=retriever)
    response = Response()
    response.status_code = 403
    response._content = EXPIRY_ERROR.encode()

    resolution = requester.error_handler.interpret_response(response)

    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error
