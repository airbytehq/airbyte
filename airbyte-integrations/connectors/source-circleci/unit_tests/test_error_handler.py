# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {
    "api_key": "test-api-key",
    "org_id": "test-org-id",
    "start_date": "2020-01-01T00:00:00Z",
    "project_id": "test-project-id",
}
CONTEXT_REQUEST = HttpRequest(
    url="https://circleci.com/api/v2/context",
    query_params={"owner-id": CONFIG["org_id"]},
    headers={"Circle-Token": CONFIG["api_key"]},
)
RATE_LIMIT_SLEEP_PADDING_SECONDS = 1


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    slept: list[float] = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: slept.append(seconds))
    return slept


def _configured_backoff_durations(sleep_durations: list[float]) -> list[float]:
    return [duration - RATE_LIMIT_SLEEP_PADDING_SECONDS for duration in sleep_durations if duration]


def _read_context(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("context", SyncMode.full_refresh).build()
    return read(get_source(), CONFIG, catalog, expecting_exception=expecting_exception)


def _resolved_manifest() -> dict[str, Any]:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = _resolved_manifest()
    composite_handlers: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "CompositeErrorHandler":
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)

    assert not composite_handlers
    for stream in manifest["definitions"]["streams"].values():
        assert stream["retriever"]["requester"]["error_handler"]["type"] == "DefaultErrorHandler"


@freeze_time("2024-03-01T00:00:00Z")
def test_context_retries_rate_limits_with_exponential_backoff(no_sleep: list[float]) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            CONTEXT_REQUEST,
            [
                HttpResponse(body=json.dumps({"message": "Rate limited"}), status_code=429),
                HttpResponse(body=json.dumps({"message": "Rate limited"}), status_code=429),
                HttpResponse(
                    body=json.dumps({"items": [{"id": "context-1", "created_at": "2024-02-01T00:00:00.000Z"}]}),
                    status_code=200,
                ),
            ],
        )

        output = _read_context()

        http_mocker.assert_number_of_calls(CONTEXT_REQUEST, 3)

    assert not output.errors
    assert len(output.records) == 1
    assert _configured_backoff_durations(no_sleep) == [4.0, 8.0]


@freeze_time("2024-03-01T00:00:00Z")
def test_context_emits_error_after_max_retries(no_sleep: list[float]) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            CONTEXT_REQUEST,
            [
                HttpResponse(body=json.dumps({"message": "Rate limited"}), status_code=429),
                HttpResponse(body=json.dumps({"message": "Rate limited"}), status_code=429),
                HttpResponse(body=json.dumps({"message": "Rate limited"}), status_code=429),
                HttpResponse(body=json.dumps({"message": "Rate limited"}), status_code=429),
                HttpResponse(body=json.dumps({"items": []}), status_code=200),
            ],
        )

        output = _read_context(expecting_exception=True)

        http_mocker.assert_number_of_calls(CONTEXT_REQUEST, 4)

    assert output.errors
    assert _configured_backoff_durations(no_sleep) == [4.0, 8.0, 16.0]
