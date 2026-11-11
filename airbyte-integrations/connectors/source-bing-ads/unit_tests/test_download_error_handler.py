# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from io import BytesIO

import pytest
import requests
from components import BingAdsDownloadErrorHandler

from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import SUCCESS_RESOLUTION


@pytest.mark.parametrize("status_code, body", [(200, b"download contents"), (204, b""), (302, b"redirect")])
def test_success_does_not_consume_download(status_code, body, mocker):
    handler = BingAdsDownloadErrorHandler(config={}, parameters={})
    delegate = mocker.patch.object(DefaultErrorHandler, "interpret_response")
    response = requests.Response()
    response.status_code = status_code
    response.raw = BytesIO(body)

    assert handler.interpret_response(response) == SUCCESS_RESOLUTION
    assert not response._content_consumed
    assert response.raw.read() == body
    delegate.assert_not_called()


@pytest.mark.parametrize("response_or_exception", [403, 500, requests.RequestException("download failed"), None])
def test_errors_delegate_to_default_handler(response_or_exception, mocker):
    handler = BingAdsDownloadErrorHandler(config={}, parameters={})
    delegate = mocker.patch.object(DefaultErrorHandler, "interpret_response")
    if isinstance(response_or_exception, int):
        response = requests.Response()
        response.status_code = response_or_exception
        response_or_exception = response

    assert handler.interpret_response(response_or_exception) is delegate.return_value
    delegate.assert_called_once_with(response_or_exception)
