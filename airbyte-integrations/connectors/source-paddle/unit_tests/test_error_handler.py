# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.models import declarative_component_schema as models
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


@pytest.fixture(scope="module")
def manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(manifest_path.read_text()))


@pytest.fixture
def error_handler(manifest: dict) -> DefaultErrorHandler:
    definition = manifest["definitions"]["base_requester"]["error_handler"]
    return ModelToComponentFactory().create_component(
        model_type=getattr(models, definition["type"]), component_definition=definition, config={}
    )


def test_all_streams_use_a_single_default_error_handler(manifest: dict) -> None:
    expected_handler = {
        "type": "DefaultErrorHandler",
        "max_retries": 5,
        "backoff_strategies": [{"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 62}],
    }
    assert manifest["definitions"]["base_requester"]["error_handler"] == expected_handler
    assert len(manifest["streams"]) == 13
    for stream in manifest["streams"]:
        assert stream["retriever"]["requester"]["error_handler"] == expected_handler, stream["name"]


@pytest.mark.parametrize(
    ("status_code", "expected_action"),
    [
        (200, ResponseAction.SUCCESS),
        (400, ResponseAction.FAIL),
        (401, ResponseAction.FAIL),
        (403, ResponseAction.FAIL),
        (404, ResponseAction.FAIL),
        (429, ResponseAction.RATE_LIMITED),
        (500, ResponseAction.RETRY),
        (502, ResponseAction.RETRY),
        (503, ResponseAction.RETRY),
        (504, ResponseAction.RETRY),
    ],
)
def test_response_classification(error_handler: DefaultErrorHandler, status_code: int, expected_action: ResponseAction) -> None:
    response = requests.Response()
    response.status_code = status_code
    response._content = b"{}"

    assert error_handler.interpret_response(response).response_action == expected_action


@pytest.mark.parametrize("exception", [requests.exceptions.Timeout(), requests.exceptions.ConnectionError()])
def test_transport_errors_are_retried(error_handler: DefaultErrorHandler, exception: requests.RequestException) -> None:
    assert error_handler.interpret_response(exception).response_action == ResponseAction.RETRY


def test_retry_limits_and_constant_backoff(error_handler: DefaultErrorHandler) -> None:
    assert error_handler.max_retries == 5
    assert error_handler.max_time == 600
    strategies = error_handler.backoff_strategies
    assert strategies is not None
    assert len(strategies) == 1
    assert [strategies[0].backoff_time(None, attempt_count=attempt) for attempt in range(6)] == [62] * 6
