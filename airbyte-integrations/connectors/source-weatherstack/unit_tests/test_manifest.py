# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.models import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


MANIFEST = yaml.safe_load((Path(__file__).resolve().parents[1] / "manifest.yaml").read_text())
STREAMS = [
    pytest.param(stream, id=f"{section}/{stream['name']}")
    for section, streams in (
        ("definitions", MANIFEST["definitions"]["streams"].values()),
        ("streams", MANIFEST["streams"]),
    )
    for stream in streams
]


@pytest.fixture(params=STREAMS)
def error_handler(request: pytest.FixtureRequest) -> DefaultErrorHandler:
    definition = request.param["retriever"]["requester"]["error_handler"]
    assert definition == {
        "type": "DefaultErrorHandler",
        "backoff_strategies": [{"type": "WaitTimeFromHeader", "header": "Retry-After"}],
    }
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})


def test_single_default_error_handler(error_handler: DefaultErrorHandler) -> None:
    assert isinstance(error_handler, DefaultErrorHandler)
    assert error_handler.max_retries == 5
    assert error_handler.max_time == 600


@pytest.mark.parametrize(
    "status_code,expected_action",
    [
        (200, ResponseAction.SUCCESS),
        (400, ResponseAction.FAIL),
        (401, ResponseAction.FAIL),
        (403, ResponseAction.FAIL),
        (404, ResponseAction.FAIL),
        (429, ResponseAction.RATE_LIMITED),
        (500, ResponseAction.RETRY),
        (503, ResponseAction.RETRY),
    ],
)
def test_response_classification(error_handler: DefaultErrorHandler, status_code: int, expected_action: ResponseAction) -> None:
    response = requests.Response()
    response.status_code = status_code
    response._content = b"{}"
    assert error_handler.interpret_response(response).response_action == expected_action


@pytest.mark.parametrize("retry_after,expected_backoff", [("12", 12), ("2.5", 2.5), (None, None), ("invalid", None)])
def test_retry_after_backoff(error_handler: DefaultErrorHandler, retry_after: str | None, expected_backoff: float | None) -> None:
    response = requests.Response()
    response.status_code = 429
    if retry_after is not None:
        response.headers["Retry-After"] = retry_after
    assert error_handler.backoff_time(response, attempt_count=1) == expected_backoff


def test_connection_error_retries(error_handler: DefaultErrorHandler) -> None:
    assert error_handler.interpret_response(requests.ConnectionError()).response_action == ResponseAction.RETRY
