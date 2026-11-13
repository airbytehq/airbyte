# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative import models
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
if not MANIFEST_PATH.exists():
    MANIFEST_PATH = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")

MANIFEST = yaml.safe_load(MANIFEST_PATH.read_text())
CONFIG = {"api_key": "test-api-key"}


def error_handlers(node: Any, path: str = "") -> Iterator[tuple[str, dict[str, Any]]]:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "error_handler":
                yield f"{path}.{key}", value
            else:
                yield from error_handlers(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from error_handlers(value, f"{path}[{index}]")


HANDLERS = list(error_handlers(MANIFEST))


def test_all_requester_handlers_are_covered() -> None:
    assert len(HANDLERS) == 26


@pytest.mark.parametrize("path,handler", HANDLERS, ids=[path for path, _ in HANDLERS])
def test_requester_uses_default_error_handler(path: str, handler: dict[str, Any]) -> None:
    assert handler == {
        "type": "DefaultErrorHandler",
        "backoff_strategies": [{"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 62}],
        "response_filters": [{"type": "HttpResponseFilter", "action": "RETRY", "http_codes": [420, 429]}],
    }, path


@pytest.mark.parametrize("path,handler", HANDLERS, ids=[path for path, _ in HANDLERS])
@pytest.mark.parametrize(
    "status_code,action",
    [
        (200, ResponseAction.SUCCESS),
        (400, ResponseAction.FAIL),
        (401, ResponseAction.FAIL),
        (404, ResponseAction.FAIL),
        (420, ResponseAction.RETRY),
        (429, ResponseAction.RETRY),
        (500, ResponseAction.RETRY),
    ],
)
def test_error_handler_preserves_response_and_backoff(path: str, handler: dict[str, Any], status_code: int, action: ResponseAction) -> None:
    component = ModelToComponentFactory().create_component(getattr(models, handler["type"]), handler, CONFIG)
    response = requests.Response()
    response.status_code = status_code
    response._content = b"{}"

    assert component.interpret_response(response).response_action == action, path
    assert component.max_retries == 5
    assert component.max_time == 600
    assert len(component.backoff_strategies) == 1
    assert component.backoff_strategies[0].backoff_time(response, attempt_count=0) == 62


def test_manifest_validates_and_constructs_streams(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=CONFIG)
    assert {stream.name for stream in source.streams(CONFIG)} == set(MANIFEST["definitions"]["streams"])
