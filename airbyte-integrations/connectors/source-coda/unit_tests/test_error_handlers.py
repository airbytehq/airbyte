# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from pathlib import Path

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models import declarative_component_schema as models
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RateLimitBackoffException
from airbyte_cdk.sources.streams.http.http_client import HttpClient


@pytest.fixture(scope="module", params=[("definitions", "content"), ("definitions", "rows"), ("streams", "content"), ("streams", "rows")])
def handler_definition(request: pytest.FixtureRequest) -> dict:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    manifest_path = (ci_path if ci_path.exists() else Path(__file__).parent.parent) / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    location, name = request.param
    stream = (
        manifest["definitions"]["streams"][name]
        if location == "definitions"
        else next(stream for stream in manifest["streams"] if stream["name"] == name)
    )
    return stream["retriever"]["requester"]["error_handler"]


@pytest.fixture
def handler(handler_definition: dict) -> DefaultErrorHandler:
    return ModelToComponentFactory().create_component(getattr(models, handler_definition["type"]), handler_definition, {})


def test_error_handler_is_a_single_default_handler(handler_definition: dict) -> None:
    assert handler_definition == {
        "type": "DefaultErrorHandler",
        "response_filters": [{"type": "HttpResponseFilter", "action": "IGNORE", "http_codes": [404]}],
    }


@pytest.mark.parametrize(
    "status, action, failure_type",
    [
        (200, ResponseAction.SUCCESS, None),
        (400, ResponseAction.FAIL, FailureType.system_error),
        (401, ResponseAction.FAIL, FailureType.config_error),
        (403, ResponseAction.FAIL, FailureType.config_error),
        (404, ResponseAction.IGNORE, FailureType.system_error),
        (429, ResponseAction.RATE_LIMITED, FailureType.transient_error),
        (500, ResponseAction.RETRY, FailureType.transient_error),
        (503, ResponseAction.RETRY, FailureType.transient_error),
    ],
)
def test_http_response_classification(
    handler: DefaultErrorHandler, status: int, action: ResponseAction, failure_type: FailureType | None
) -> None:
    response = requests.Response()
    response.status_code = status
    response._content = b'{"message": "test error"}'
    resolution = handler.interpret_response(response)
    assert resolution.response_action == action
    assert resolution.failure_type == failure_type
    assert handler.max_retries == 5
    assert handler.max_time == 600


def test_connection_error_is_retried(handler: DefaultErrorHandler) -> None:
    resolution = handler.interpret_response(requests.ConnectionError("test connection error"))
    assert resolution.response_action == ResponseAction.RETRY
    assert resolution.failure_type == FailureType.system_error
    assert resolution.error_message == "ConnectionError: test connection error"


@pytest.mark.parametrize(
    "status, exception", [(429, RateLimitBackoffException), (500, DefaultBackoffException), (503, DefaultBackoffException)]
)
def test_http_client_uses_default_backoff(handler: DefaultErrorHandler, status: int, exception: type[Exception]) -> None:
    client = HttpClient(
        name="test",
        logger=logging.getLogger("test"),
        error_handler=handler,
        backoff_strategy=handler.backoff_strategies,
    )
    response = requests.Response()
    response.status_code = status
    response.request = requests.Request("GET", "https://coda.io/apis/v1/test").prepare()
    client._request_attempt_count[response.request] = 1
    with pytest.raises(exception):
        client._handle_error_resolution(response, None, response.request, handler.interpret_response(response))
