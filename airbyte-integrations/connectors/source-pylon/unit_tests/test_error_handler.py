# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.models import declarative_component_schema as models
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


@pytest.fixture
def error_handler(manifest_path: Path):
    manifest = yaml.safe_load(manifest_path.read_text())
    definition = manifest["definitions"]["error_handler"]
    return ModelToComponentFactory().create_component(
        model_type=getattr(models, definition["type"]), component_definition=definition, config={}
    )


def test_streams_use_the_shared_default_error_handler(manifest_path: Path) -> None:
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(manifest_path.read_text()))
    expected_handler = {
        "type": "DefaultErrorHandler",
        "max_retries": 3,
        "backoff_strategies": [{"type": "ExponentialBackoffStrategy", "factor": 5}],
        "response_filters": [
            {"type": "HttpResponseFilter", "action": "RATE_LIMITED", "http_codes": [429], "error_message": "Rate limit hit"}
        ],
    }
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
    ],
)
def test_response_classification(error_handler, status_code: int, expected_action: ResponseAction) -> None:
    response = requests.Response()
    response.status_code = status_code
    response._content = b"{}"

    resolution = error_handler.interpret_response(response)

    assert resolution.response_action == expected_action
    if status_code == 429:
        assert resolution.error_message == "Rate limit hit"


def test_retry_limit_and_exponential_backoff(error_handler) -> None:
    assert error_handler.max_retries == 3
    assert len(error_handler.backoff_strategies) == 1
    strategy = error_handler.backoff_strategies[0]
    assert [strategy.backoff_time(None, attempt_count=attempt) for attempt in range(3)] == [5, 10, 20]
