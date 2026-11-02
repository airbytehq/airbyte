# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the per-stream rate-limit error handler in `source-gorgias`."""

from unittest.mock import patch

import pytest
import requests
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import WaitTimeFromHeaderBackoffStrategy
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "username": "test-username",
    "password": "test-password",
    "domain_name": "test-domain",
    "start_date": "2026-01-01T00:00:00Z",
}


def _stream_requesters():
    source = get_source(config=_CONFIG)
    for stream in source.streams(_CONFIG):
        retriever = stream._stream_partition_generator._partition_factory._retriever
        yield stream.name, retriever.requester


def _response(status_code: int) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.headers["Retry-after"] = "7"
    return response


@pytest.mark.parametrize("stream_name,requester", list(_stream_requesters()))
def test_stream_uses_single_rate_limit_error_handler(stream_name, requester):
    error_handler = requester.error_handler

    assert isinstance(error_handler, DefaultErrorHandler), stream_name
    assert error_handler.max_retries == 3
    assert len(error_handler.backoff_strategies) == 1
    backoff_strategy = error_handler.backoff_strategies[0]
    assert isinstance(backoff_strategy, WaitTimeFromHeaderBackoffStrategy)
    assert backoff_strategy.backoff_time(_response(429), attempt_count=1) == 7

    resolution = error_handler.interpret_response(_response(429))
    assert resolution.response_action == ResponseAction.RATE_LIMITED
    assert resolution.error_message == "Rate limits hit"


def test_account_stream_retries_after_rate_limit():
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream("account", SyncMode.full_refresh).build()

    with requests_mock.Mocker() as mocker, patch("time.sleep") as mock_sleep:
        mocker.get(
            "https://test-domain.gorgias.com/api/account",
            [
                {"status_code": 429, "headers": {"Retry-after": "1"}, "json": {}},
                {"status_code": 200, "json": {"domain": "test-domain"}},
            ],
        )
        output = read(source, _CONFIG, catalog)

    assert [record.record.data["domain"] for record in output.records] == ["test-domain"]
    assert mocker.call_count == 2
    mock_sleep.assert_called()
