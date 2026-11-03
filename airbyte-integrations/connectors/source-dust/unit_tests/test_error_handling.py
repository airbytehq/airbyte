# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models import declarative_component_schema as models
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


STREAMS = ["usage_metrics", "active_users", "source", "tool_usage", "skill_usage", "agents", "users", "messages"]


@pytest.fixture(params=STREAMS)
def handler_definition(request: pytest.FixtureRequest, resolved_manifest: dict) -> dict:
    stream = next(stream for stream in resolved_manifest["streams"] if stream["name"] == request.param)
    return stream["retriever"]["requester"]["error_handler"]


@pytest.fixture
def handler(handler_definition: dict):
    model = getattr(models, handler_definition["type"])
    return ModelToComponentFactory().create_component(model, handler_definition, config={})


def response(status_code: int, body: bytes = b'{}') -> requests.Response:
    result = requests.Response()
    result.status_code = status_code
    result.request = requests.Request("GET", "https://dust.tt/api/v1/w/test/analytics/export").prepare()
    result.url = result.request.url
    result.headers["Content-Type"] = "application/json"
    result._content = body
    return result


def test_401_fails_fast_as_config_error(handler) -> None:
    resolution = handler.interpret_response(response(401))
    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error


@pytest.mark.parametrize("status_code", [429, 500, 502, 503, 504])
@pytest.mark.parametrize("body", [b'{}', b''])
def test_transient_errors_retry(handler, status_code: int, body: bytes) -> None:
    assert handler.interpret_response(response(status_code, body)).response_action == ResponseAction.RETRY


@pytest.mark.parametrize("status_code", [400, 403, 404])
def test_client_errors_fail(handler, status_code: int) -> None:
    assert handler.interpret_response(response(status_code)).response_action == ResponseAction.FAIL


def test_success_is_not_retried(handler) -> None:
    assert handler.interpret_response(response(200, b'[]')).response_action == ResponseAction.SUCCESS


def test_retry_policy(handler_definition: dict, handler) -> None:
    assert handler.max_retries == 3
    assert handler_definition["backoff_strategies"] == [{"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 30}]


def test_stream_uses_single_shared_handler(handler_definition: dict, manifest: dict) -> None:
    assert handler_definition["type"] == "DefaultErrorHandler"
    assert handler_definition == manifest["definitions"]["error_handler"]
    assert len(manifest["streams"]) == len(STREAMS)
    for stream in manifest["streams"]:
        assert stream["retriever"]["requester"]["error_handler"] == {"$ref": "#/definitions/error_handler"}


def test_manifest_has_no_composite_error_handler(manifest: dict) -> None:
    assert "CompositeErrorHandler" not in str(manifest)
