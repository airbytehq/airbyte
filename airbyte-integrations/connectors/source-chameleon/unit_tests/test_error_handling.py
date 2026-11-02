# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any

import pytest
import requests_mock
import yaml
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_STREAM_NAMES = [
    pytest.param("helpbars", id="helpbars"),
    pytest.param("segments", id="segments"),
    pytest.param("urls", id="urls"),
    pytest.param("url_groups", id="url_groups"),
    pytest.param("changes", id="changes"),
    pytest.param("launchers", id="launchers"),
    pytest.param("tooltips", id="tooltips"),
    pytest.param("tours", id="tours"),
    pytest.param("surveys", id="surveys"),
    pytest.param("survey_responses", id="survey_responses"),
]
_CONFIG = {
    "api_key": "test",
    "start_date": "2024-01-01T00:00:00Z",
    "limit": "50",
    "end_date": "2024-01-31T00:00:00Z",
}
_SEGMENTS_URL = "https://api.chameleon.io/v3/edit/segments"
_SEGMENTS_RESPONSE = {
    "segments": [{"id": "segment-1", "updated_at": "2024-01-02T00:00:00.000Z"}],
}
_EXPECTED_ERROR_HANDLER = {
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


@pytest.fixture
def manifest() -> dict[str, Any]:
    return yaml.safe_load(_MANIFEST_PATH.read_text())


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_rate_limit_error_handler_is_default(stream_name: str, manifest: dict[str, Any]) -> None:
    error_handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler == _EXPECTED_ERROR_HANDLER


def test_manifest_builds_all_streams() -> None:
    streams = get_source(_CONFIG).streams(_CONFIG)

    assert len(streams) == 10


def _read_segments(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("segments", SyncMode.full_refresh).build()
    return read(
        get_source(_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


def test_rate_limit_retries_then_reads_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)

    with requests_mock.Mocker() as mocker:
        mocker.get(
            _SEGMENTS_URL,
            [
                {"status_code": 429, "json": {"error": "Rate limit"}},
                {"status_code": 200, "json": _SEGMENTS_RESPONSE},
            ],
        )
        output = _read_segments()

        requests_made = [request for request in mocker.request_history if request.path == "/v3/edit/segments"]

    assert output.errors == []
    assert len(output.records) == 1
    assert len(requests_made) == 2


def test_rate_limit_exhausts_retries_and_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)

    with requests_mock.Mocker() as mocker:
        mocker.get(_SEGMENTS_URL, status_code=429, json={"error": "Rate limit"})
        output = _read_segments(expecting_exception=True)

        requests_made = [request for request in mocker.request_history if request.path == "/v3/edit/segments"]

    assert output.records == []
    assert output.errors
    assert len(requests_made) == 4
