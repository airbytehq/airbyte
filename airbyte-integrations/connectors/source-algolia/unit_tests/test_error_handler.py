# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
STREAM_NAMES = ("indices", "indexes_query", "available_languages", "logs", "indexes_settings")
CONFIG = {
    "application_id": "test-application",
    "api_key": "test-key",
    "start_date": "2024-01-01T00:00:00Z",
    "search_query": "test",
}


@pytest.fixture(scope="module")
def manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text())


@pytest.fixture(params=STREAM_NAMES)
def handler_definition(request: pytest.FixtureRequest, manifest: dict) -> dict:
    resolved = ManifestReferenceResolver().preprocess_manifest(manifest)
    return resolved["definitions"]["streams"][request.param]["retriever"]["requester"]["error_handler"]


@pytest.fixture
def handler(handler_definition: dict) -> DefaultErrorHandler:
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, handler_definition, CONFIG)


def test_manifest_handlers_use_single_default_handler(handler_definition: dict) -> None:
    assert handler_definition == {
        "type": "DefaultErrorHandler",
        "max_retries": 3,
        "backoff_strategies": [{"type": "ExponentialBackoffStrategy", "factor": 2}],
        "response_filters": [
            {
                "type": "HttpResponseFilter",
                "action": "RATE_LIMITED",
                "http_codes": [429],
                "error_message": "Rate limits hit",
            }
        ],
    }


def test_manifest_builds_all_streams(manifest: dict, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    source = ConcurrentDeclarativeSource(source_config=manifest, config=CONFIG, catalog=None, state=None)
    assert {stream.name for stream in source.streams(CONFIG)} == set(STREAM_NAMES)


def test_retry_limits_and_exponential_backoff(handler: DefaultErrorHandler) -> None:
    assert handler.max_retries == 3
    assert handler.max_time == 600
    assert handler.backoff_strategies is not None
    assert len(handler.backoff_strategies) == 1
    assert [handler.backoff_strategies[0].backoff_time(None, attempt) for attempt in range(4)] == [2, 4, 8, 16]


@pytest.mark.parametrize(
    "status_code,expected_action",
    [
        (200, ResponseAction.SUCCESS),
        (400, ResponseAction.FAIL),
        (401, ResponseAction.FAIL),
        (403, ResponseAction.FAIL),
        (404, ResponseAction.FAIL),
        (408, ResponseAction.RETRY),
        (429, ResponseAction.RATE_LIMITED),
        (500, ResponseAction.RETRY),
        (502, ResponseAction.RETRY),
        (503, ResponseAction.RETRY),
        (504, ResponseAction.RETRY),
    ],
)
def test_response_classification(handler: DefaultErrorHandler, status_code: int, expected_action: ResponseAction) -> None:
    response = requests.Response()
    response.status_code = status_code
    resolution = handler.interpret_response(response)
    assert resolution.response_action == expected_action
    if status_code == 429:
        assert resolution.error_message == "Rate limits hit"


def test_connection_errors_are_retried(handler: DefaultErrorHandler) -> None:
    assert handler.interpret_response(requests.ConnectionError("connection interrupted")).response_action == ResponseAction.RETRY
