# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative import models
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler


STREAM_NAMES = ["addresses", "banks", "postcards", "templates", "templates_versions", "campaigns", "uploads", "qr_code_analytics"]
MANIFEST_PATH = Path(__file__).resolve().parents[1] / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest() -> dict[str, Any]:
    return yaml.safe_load(MANIFEST_PATH.read_text())


@pytest.fixture(params=STREAM_NAMES)
def requester(request: pytest.FixtureRequest, manifest: dict[str, Any]) -> dict[str, Any]:
    return manifest["definitions"]["streams"][request.param]["retriever"]["requester"]


@pytest.fixture
def error_handler(requester: dict[str, Any]) -> ErrorHandler:
    definition = requester["error_handler"]
    return ModelToComponentFactory().create_component(
        model_type=getattr(models, definition["type"]), component_definition=definition, config={}
    )


def test_requester_uses_default_error_handler_directly(requester: dict[str, Any]) -> None:
    assert requester["$ref"] == "#/definitions/base_requester"
    assert requester["error_handler"] == {
        "type": "DefaultErrorHandler",
        "max_retries": 3,
        "backoff_strategies": [{"type": "ExponentialBackoffStrategy", "factor": 2}],
        "response_filters": [
            {"type": "HttpResponseFilter", "action": "RATE_LIMITED", "http_codes": [429], "error_message": "Rate limits hit"}
        ],
    }


@pytest.mark.parametrize(
    "status_code,expected_action",
    [(200, "SUCCESS"), (400, "FAIL"), (401, "FAIL"), (404, "FAIL"), (429, "RATE_LIMITED"), (500, "RETRY")],
)
def test_error_classification(error_handler: ErrorHandler, status_code: int, expected_action: str) -> None:
    response = requests.Response()
    response.status_code = status_code
    response._content = b"{}"

    resolution = error_handler.interpret_response(response)

    assert resolution.response_action is not None
    assert resolution.response_action.value == expected_action
    if status_code == 429:
        assert resolution.error_message == "Rate limits hit"


def test_retry_limits_and_backoff(error_handler: ErrorHandler) -> None:
    assert isinstance(error_handler, DefaultErrorHandler)
    assert error_handler.max_retries == 3
    assert error_handler.max_time == 600
    assert error_handler.backoff_strategies is not None
    assert len(error_handler.backoff_strategies) == 1
    strategy = error_handler.backoff_strategies[0]
    assert [strategy.backoff_time(None, attempt_count=attempt) for attempt in range(3)] == [2, 4, 8]


def test_network_timeout_is_retried(error_handler: ErrorHandler) -> None:
    resolution = error_handler.interpret_response(requests.exceptions.Timeout())
    assert resolution.response_action is not None
    assert resolution.response_action.value == "RETRY"
