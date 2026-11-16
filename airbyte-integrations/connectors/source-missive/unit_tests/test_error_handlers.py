# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.models import declarative_component_schema as models
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


STREAM_NAMES = (
    "contact_books",
    "contacts",
    "contact_groups",
    "users",
    "teams",
    "shared_labels",
    "organizations",
    "conversations",
)
CONFIG = {"api_key": "test-api-key", "start_date": "2024-01-01T00:00:00Z"}


@pytest.fixture(scope="module")
def manifest() -> dict[str, Any]:
    manifest_folder = Path("/airbyte/integration_code/source_declarative_manifest")
    if not manifest_folder.exists():
        manifest_folder = Path(__file__).parent.parent
    return yaml.safe_load((manifest_folder / "manifest.yaml").read_text())


@pytest.fixture(scope="module")
def handlers(manifest: dict[str, Any]) -> dict[str, ErrorHandler]:
    factory = ModelToComponentFactory()
    handlers_by_stream = {}
    for stream_name in STREAM_NAMES:
        handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]
        handlers_by_stream[stream_name] = factory.create_component(getattr(models, handler["type"]), handler, CONFIG)
    return handlers_by_stream


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_single_default_handler(manifest: dict[str, Any], stream_name: str) -> None:
    handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]
    assert handler == {
        "type": "DefaultErrorHandler",
        "max_retries": 3,
        "backoff_strategies": [{"type": "ExponentialBackoffStrategy", "factor": 2}],
        "response_filters": [
            {"type": "HttpResponseFilter", "action": "RATE_LIMITED", "http_codes": [429], "error_message": "Rate limit hit"}
        ],
    }


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_retry_limits_and_backoff(handlers: dict[str, ErrorHandler], stream_name: str) -> None:
    handler = handlers[stream_name]
    assert handler.max_retries == 3
    assert handler.max_time == 600
    assert len(handler.backoff_strategies) == 1
    backoff = handler.backoff_strategies[0]
    assert isinstance(backoff, ExponentialBackoffStrategy)
    for attempt_count in range(1, 4):
        assert backoff.backoff_time(None, attempt_count=attempt_count) == 2 * 2**attempt_count


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
@pytest.mark.parametrize(
    "status_code, expected_action",
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
def test_response_classification(
    handlers: dict[str, ErrorHandler], stream_name: str, status_code: int, expected_action: ResponseAction
) -> None:
    response = requests.Response()
    response.status_code = status_code
    resolution = handlers[stream_name].interpret_response(response)
    assert resolution.response_action == expected_action
    if status_code == 429:
        assert resolution.error_message == "Rate limit hit"
