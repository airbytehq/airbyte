# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.models.declarative_component_schema import HttpRequester as HttpRequesterModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


MANIFEST = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load((Path(__file__).parents[1] / "manifest.yaml").read_text()))
STREAM_NAMES = list(MANIFEST["definitions"]["streams"])
CONFIG = {"api_key": "test-api-key", "start_date": "2025-01-01T00:00:00Z"}


@pytest.fixture(params=STREAM_NAMES)
def requester_definition(request: pytest.FixtureRequest) -> dict[str, Any]:
    return MANIFEST["definitions"]["streams"][request.param]["retriever"]["requester"]


@pytest.fixture
def requester(requester_definition: dict[str, Any]) -> HttpRequester:
    return ModelToComponentFactory().create_component(HttpRequesterModel, requester_definition, CONFIG, name="test")


def test_single_default_error_handler(requester_definition: dict[str, Any], requester: HttpRequester) -> None:
    assert requester_definition["error_handler"] == {
        "type": "DefaultErrorHandler",
        "max_retries": 3,
        "backoff_strategies": [{"type": "ExponentialBackoffStrategy", "factor": 2}],
        "response_filters": [
            {"type": "HttpResponseFilter", "action": "RATE_LIMITED", "http_codes": [429], "error_message": "Rate limits hit"}
        ],
    }
    assert isinstance(requester.error_handler, DefaultErrorHandler)
    assert requester.error_handler.max_retries == 3


@pytest.mark.parametrize(
    "status_code, expected_action",
    [
        (200, ResponseAction.SUCCESS),
        (400, ResponseAction.FAIL),
        (401, ResponseAction.FAIL),
        (429, ResponseAction.RATE_LIMITED),
        (500, ResponseAction.RETRY),
    ],
)
def test_response_classification(requester: HttpRequester, status_code: int, expected_action: ResponseAction) -> None:
    response = requests.Response()
    response.status_code = status_code
    assert requester.error_handler is not None
    resolution = requester.error_handler.interpret_response(response)

    assert resolution.response_action == expected_action
    if status_code == 429:
        assert resolution.error_message == "Rate limits hit"


@pytest.mark.parametrize("attempt_count, expected_delay", [(0, 2), (1, 4), (2, 8), (3, 16)])
def test_exponential_backoff(requester: HttpRequester, attempt_count: int, expected_delay: int) -> None:
    response = requests.Response()
    response.status_code = 429
    assert isinstance(requester.error_handler, DefaultErrorHandler)
    assert requester.error_handler.backoff_strategies
    strategy = requester.error_handler.backoff_strategies[0]

    assert strategy.backoff_time(response, attempt_count=attempt_count) == expected_delay
